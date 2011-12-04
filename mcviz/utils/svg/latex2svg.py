"""
latex2svg.py
functions for converting LaTeX equation string into SVG path
This extension need, to work properly:
    - a TeX/LaTeX distribution (MiKTeX ...)
    - pstoedit software: <http://www.pstoedit.net/pstoedit>

Parts of this file Copyright (C) 2006 Julien Vitard <julienvitard@gmail.com>
Copyright (C) 2011 Johannes Ebke <ebke@cern.ch>; Peter Waller

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA
"""

import os
import sys
import tempfile
from textwrap import dedent
from xml.dom import minidom
from shutil import rmtree

def process_path_data(d, tf_x, tf_y):
    x_positions = []
    y_positions = []

    # treat Polygon data here
    if d[0] != "M":
        new_points = []
        for pt in d.split():
            x, y = map(float, pt.split(","))
            x = tf_x(x)
            y = tf_y(y)
            x_positions.append(x)
            y_positions.append(y)
            new_points.append("%.2f,%.2f" % (x, y))
        return (" ".join(new_points), min(x_positions), max(x_positions), 
                                      min(y_positions), max(y_positions))

    # split and preprocess command strings
    cmds = []
    for cmdstr in d.strip().split(" "):
        if cmdstr[0] == "Z":
            numbers = []
        else:
            numbers = map(float, cmdstr[1:].split(","))
        cmds.append((cmdstr[0], numbers))

    # Trace the pen and relativize svg
    x0, y0 = cmds[0][1][0], cmds[0][1][1]
    x0, y0 = tf_x(x0), tf_y(y0)
    x_positions.append(x0)
    y_positions.append(y0)

    out = ["M%.2f,%.2f" % (x0, y0)]
    for cmd, numbers in cmds[1:]:
        if cmd == "H":
            numbers[0] = tf_x(numbers[0])
            x_positions.append(numbers[0])
            numbers[0] -= x0
            x0 += numbers[0]
        elif cmd == "V":
            numbers[0] = tf_y(numbers[0])
            y_positions.append(numbers[0])
            numbers[0] -= y0
            y0 += numbers[0]
        else:
            for i in range(len(numbers)/2):
                numbers[2*i] = tf_x(numbers[2*i]) - x0
                numbers[2*i+1] = tf_y(numbers[2*i + 1]) - y0
            if numbers:
                x_positions.append(numbers[-2] + x0)
                y_positions.append(numbers[-1] + y0)
                x0 += numbers[-2]
                y0 += numbers[-1]
        nstr = (",".join(["%.2f"]*len(numbers))) % tuple(numbers)
        out.append("%s%s" % (cmd.lower(),nstr))
    return " ".join(out), min(x_positions), max(x_positions), min(y_positions), max(y_positions)


class Latex2SVG(object):
    def __init__(self, id, content):
        self.id = id
        self.content = content
        self.xmin = self.xmax = None
        self.ymin = self.ymax = None
        self.dom = None
        self.xml = None
        self.build_svg()

    @property
    def dimensions(self):
        """Returns width and height of glyph"""
        xwidth = self.xmax - self.xmin
        ywidth = self.ymax - self.ymin
        return xwidth, ywidth

    def dom2xml(self):
        self.xml = self.dom.toxml()
        self.dom = None

    def write_tex_file(self, filename):
        with open(filename, "w") as fd:
            fd.write(dedent(r"""
                %% processed with eqtexsvg.py
                \documentclass{article}
                \usepackage{amsmath}
                \usepackage{amssymb}
                \usepackage{amsfonts}

                \thispagestyle{empty}
                \begin{document}
                \begin{center}%s\end{center}
                \end{document}
            """ % self.content).strip())



    def build_svg(self, use_pdf = True):
        base_dir = tempfile.mkdtemp("", "latex2svg-");
        latex_file = os.path.join(base_dir, "eq.tex")
        aux_file = os.path.join(base_dir, "eq.aux")
        log_file = os.path.join(base_dir, "eq.log")
        if use_pdf:
            texout_file = os.path.join(base_dir, "eq.pdf")
            ps_file = os.path.join(base_dir, "eq.ps")
            pdf_file = texout_file
        else:
            texout_file = os.path.join(base_dir, "eq.dvi")
            ps_file = os.path.join(base_dir, "eq.ps")
        svg_file = os.path.join(base_dir, "eq.svg")
        out_file = os.path.join(base_dir, "eq.out")
        err_file = os.path.join(base_dir, "eq.err")

        def clean():
            rmtree(base_dir)

        self.write_tex_file(latex_file)
        os.system('%slatex "-output-directory=%s" -halt-on-error "%s" > "%s"'
                  % ("pdf" if use_pdf else "", base_dir, latex_file, out_file))
                  
        try:
            os.stat(texout_file)
        except OSError:
            print >>sys.stderr, "invalid LaTeX input:"
            print >>sys.stderr, self.content
            print >>sys.stderr, "temporary files were left in:", base_dir
            raise

        if not use_pdf:
            os.system('dvips -q -f -E -D 600 -y 5000 -o "%s" "%s"' % (ps_file, texout_file))
        else:
            os.system('pdftops "%s" "%s"' % (pdf_file, ps_file))

        # cd to base_dir is necessary, because pstoedit writes
        # temporary files to cwd and needs write permissions
        separator = ';'
        if os.name == 'nt':
            separator = '&&'
        os.system('cd "%s" %s pstoedit -f plot-svg -dt -ssp "%s" "%s" > "%s" 2> "%s"'
                  % (base_dir, separator, ps_file, svg_file, out_file, err_file))

        # forward errors to stderr but skip pstoedit header
        if os.path.exists(err_file):
            err_stream = open(err_file, 'r')
            for line in err_stream:
                if not line.startswith('pstoedit: version'):
                    sys.stderr.write(line + '\n')
            err_stream.close()
 
        self.process_svg_file(svg_file)

        clean()

    def process_svg_file(self, filename):
        # scale set to 10 to avoid resolution effects with %.2f
        scale = 10
        # constants derived from experience
        shift_x = -305.22
        shift_y = 709.75

        def tf_x(x):
            return (  x + shift_x) * scale
        def tf_y(y):
            # This minus sign is here on purpose, the input svg is flipped
            return (- y + shift_y) * scale

        def report_x(x):
            if self.xmin is None:
                self.xmin = x
            if self.xmax is None:
                self.xmax = x
            self.xmin, self.xmax = min(x, self.xmin), max(x, self.xmax)

        def report_y(y):
            if self.ymin is None:
                self.ymin = y
            if self.ymax is None:
                self.ymax = y
            self.ymin, self.ymax = min(y, self.ymin), max(y, self.ymax)

        def clone_and_rewrite(self, node_in):
            in_tag = node_in.nodeName
            if in_tag != 'svg':
                node_out = minidom.Element(in_tag)
                for name, value in node_in.attributes.items():
                    node_out.setAttribute(name, value)
            else:
                node_out = minidom.Element("svg")

            for c in node_in.childNodes:
                if c.nodeName not in ('g', 'path', 'polyline', 'polygon', 'line'):
                    continue
                    
                child = clone_and_rewrite(self, c)
                
                if c.nodeName == 'g':
                    child.removeAttribute("transform")
                    child.setAttribute('id', str(self.id))
                elif c.nodeName == 'path' or c.nodeName == 'polygon':
                    if c.nodeName == 'path':
                        data_attr = "d"
                    else:
                        data_attr = "points"
                    data = c.getAttribute(data_attr)
                    d, x0, x1, y0, y1 = process_path_data(data, tf_x, tf_y)
                    child.setAttribute(data_attr, d)
                    report_x(x0)
                    report_x(x1)
                    report_y(y0)
                    report_y(y1)
                elif c.nodeName == 'line':
                    width = float(child.getAttribute("stroke-width")) * scale
                    for attr in ("x1", "x2"):
                        x = tf_x(float(child.getAttribute(attr)))
                        report_x(x)
                        child.setAttribute(attr, "%.2f" % x)
                    for attr in ("y1", "y2"):
                        y = tf_y(float(child.getAttribute(attr)))
                        report_y(y)
                        child.setAttribute(attr, "%.2f" % y)
                    child.setAttribute("stroke-width", "%.2f" % width)

                node_out.appendChild(child)
                
            return node_out

        doc = minidom.parse(filename)
        svg = [cn for cn in doc.childNodes if cn.childNodes][0]
        self.dom = clone_and_rewrite(self, svg).childNodes[0]

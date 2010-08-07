#!/usr/bin/env python
# -*- coding: cp1252 -*-
"""
eqtexsvg.py
functions for converting LaTeX equation string into SVG path
This extension need, to work properly:
    - a TeX/LaTeX distribution (MiKTeX ...)
    - pstoedit software: <http://www.pstoedit.net/pstoedit>

Copyright (C) 2006 Julien Vitard <julienvitard@gmail.com>
Heavily modified 2010 Johannes Ebke <ebke@cern.ch>

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

import os, tempfile, sys, xml.dom.minidom

class TexGlyph(object):
    def __init__(self, formula, name):
        self.formula = formula
        self.name = name

    def get_svg(self):
        base_dir = tempfile.mkdtemp("", "glyphsvg-");
        latex_file = os.path.join(base_dir, "eq.tex")
        aux_file = os.path.join(base_dir, "eq.aux")
        log_file = os.path.join(base_dir, "eq.log")
        ps_file = os.path.join(base_dir, "eq.ps")
        dvi_file = os.path.join(base_dir, "eq.dvi")
        svg_file = os.path.join(base_dir, "eq.svg")
        out_file = os.path.join(base_dir, "eq.out")
        err_file = os.path.join(base_dir, "eq.err")

        def clean():
            os.remove(latex_file)
            os.remove(aux_file)
            os.remove(log_file)
            os.remove(ps_file)
            os.remove(dvi_file)
            os.remove(svg_file)
            os.remove(out_file)
            if os.path.exists(err_file):
                os.remove(err_file)
            os.rmdir(base_dir)

        self.create_equation_tex(latex_file)
        os.system('latex "-output-directory=%s" -halt-on-error "%s" > "%s"' \
                  % (base_dir, latex_file, out_file))
        try:
            os.stat(dvi_file)
        except OSError:
            print >>sys.stderr, "invalid LaTeX input:"
            print >>sys.stderr, self.options.formula
            print >>sys.stderr, "temporary files were left in:", base_dir
            raise

        os.system('dvips -q -f -E -D 600 -y 5000 -o "%s" "%s"' % (ps_file, dvi_file))

        # cd to base_dir is necessary, because pstoedit writes
        # temporary files to cwd and needs write permissions
        separator = ';'
        if os.name == 'nt':
            separator = '&&'
        os.system('cd "%s" %s pstoedit -f plot-svg -dt -ssp "%s" "%s" > "%s" 2> "%s"' \
                  % (base_dir, separator, ps_file, svg_file, out_file, err_file))

        # forward errors to stderr but skip pstoedit header
        if os.path.exists(err_file):
            err_stream = open(err_file, 'r')
            for line in err_stream:
                if not line.startswith('pstoedit: version'):
                    sys.stderr.write(line + '\n')
            err_stream.close()
 
        res = self.svg_open(svg_file)

        clean()

        return res

    def get_def(self):
        dom = self.get_svg()
        return dom.childNodes[0]

    def create_equation_tex(self, filename):
        tex = open(filename, 'w')
        tex.write("""%% processed with eqtexsvg.py
    \\documentclass{article}
    \\usepackage{amsmath}
    \\usepackage{amssymb}
    \\usepackage{amsfonts}

    \\thispagestyle{empty}
    \\begin{document}
    """)
        tex.write(self.formula)
        tex.write("\n\\end{document}\n")
        tex.close()

    def svg_open(self, filename):
        doc_sizeH = 100
        doc_sizeW = 100

        def clone_and_rewrite(self, node_in):
            in_tag = node_in.nodeName
            if in_tag != 'svg':
                node_out = xml.dom.minidom.Element(in_tag)
                for name, value in node_in.attributes.items():
                    node_out.setAttribute(name, value)
            else:
                node_out = xml.dom.minidom.Element("svg")
                node_out.setAttribute("viewBox","0 0 %s %s" % (doc_sizeH, doc_sizeW))
                node_out.setAttribute("xmlns", "http://www.w3.org/2000/svg")
                node_out.setAttribute("xmlns:xlink", "http://www.w3.org/1999/xlink")
                node_out.setAttribute("version", "1.1")

            for c in node_in.childNodes:
                c_tag = c.nodeName
                if c_tag in ('g', 'path', 'polyline', 'polygon'):
                    child = clone_and_rewrite(self, c)
                    if c_tag == 'g':
                        child.setAttribute('transform','matrix('+str(doc_sizeH/700.)+',0,0,'+str(-doc_sizeH/700.)+','+str(-doc_sizeH*0.25)+','+str(doc_sizeW*0.75)+')')
                        child.setAttribute('id', self.name)
                    node_out.appendChild(child)
            return node_out

        doc = xml.dom.minidom.parse(filename)
        svg = [cn for cn in doc.childNodes if cn.childNodes][0]
        group = clone_and_rewrite(self, svg)
        return group

if __name__ == '__main__':
    e = TexGlyph("$\\bar{K}^{++}$", "barKpp")
    print e.get_svg().toprettyxml()
    #print e.get_def().toprettyxml()
    



# vim: expandtab shiftwidth=4 tabstop=8 softtabstop=4 encoding=utf-8 textwidth=99

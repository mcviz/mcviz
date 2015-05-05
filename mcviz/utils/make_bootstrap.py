#! /usr/bin/env python
"""Produce the mcviz bootstrap script"""

import virtualenv, textwrap

OUTPUT = virtualenv.create_bootstrap_script(textwrap.dedent("""
    import os, subprocess
    from os import symlink
    def after_install(options, home_dir):

        os.system("git submodule update --init mcviz.examples")
        os.system("git submodule update --init mcviz.jet")
        try:
            symlink("mcviz.examples/mcviz/examples/inputs", "examples")
        except OSError:
            pass

        ret = subprocess.call([join(home_dir, 'bin', 'pip'), 'install', '-e', '.'])

        try:
            symlink("env/bin/mcviz", "mcv")
        except OSError:
            pass

        if not ret:
            print "Finished! Now to run mcviz, type ./mcv"

    def no_graphviz():
        print "Graphviz not installed!"
        print "Please install graphviz from http://www.graphviz.org/Download.php"
        exit(1)

    def adjust_options(options, args):
        try:
            print "Graphviz 'dot' path:"
            if os.system("which dot") != 0:
                no_graphviz()
        except OSError:
            no_graphviz()

        args[:] = ["env"]
"""))
open('mcviz_bootstrap.py', 'w').write(OUTPUT)

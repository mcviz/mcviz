#! /usr/bin/env python

import virtualenv, textwrap

output = virtualenv.create_bootstrap_script(textwrap.dedent("""
    import os, subprocess
    def after_install(options, home_dir):
        subprocess.call([join(home_dir, 'bin', 'pip'), 'install', '-e', '.'])
    
    def adjust_options(options, args):
        args[:] = ["env"]
"""))
f = open('mcviz_bootstrap.py', 'w').write(output)

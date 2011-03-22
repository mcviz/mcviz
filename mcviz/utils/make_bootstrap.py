#! /usr/bin/env python

import virtualenv, textwrap

output = virtualenv.create_bootstrap_script(textwrap.dedent("""
    import os, subprocess
    from os import symlink
    def after_install(options, home_dir):
        subprocess.call([join(home_dir, 'bin', 'pip'), 'install', '-e', '.'])
        
        try:
            symlink("env/bin/mcviz", "mcv")
        except OSError:
            pass
            
        print "Finished! Now to run mcviz, type ./mcv"
    
    def adjust_options(options, args):
        args[:] = ["env"]
"""))
f = open('mcviz_bootstrap.py', 'w').write(output)

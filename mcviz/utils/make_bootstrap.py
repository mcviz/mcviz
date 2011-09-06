#! /usr/bin/env python

import virtualenv, textwrap

output = virtualenv.create_bootstrap_script(textwrap.dedent("""
    import os, subprocess
    from os import symlink
    def after_install(options, home_dir):
        ret = subprocess.call([join(home_dir, 'bin', 'pip'), 'install', '-e', '.'])
        
        try:
            symlink("env/bin/mcviz", "mcv")
        except OSError:
            pass
        
        if not ret:
            print "Finished! Now to run mcviz, type ./mcv"
    
    def adjust_options(options, args):
        options.use_distribute = True
        options.never_download = True
        options.search_dirs.append("dist/")
        args[:] = ["env"]
"""))
f = open('mcviz_bootstrap.py', 'w').write(output)

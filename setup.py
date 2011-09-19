import sys

if not sys.version_info >= (2, 6):
    raise RuntimeError("mcviz is only compatible with python >= 2.6")

from setuptools import setup, find_packages
from textwrap import dedent

from os.path import dirname, exists, join as pjoin
from inspect import getfile
setup_location = dirname(getfile(sys.modules[__name__]))
version_file = pjoin(setup_location, "mcviz", "VERSION")
if not exists(version_file):
    raise RuntimeError("mcviz/VERSION doesn't exist!")

with open(version_file) as fd:
    version = fd.read().strip()

setup(name='mcviz',
      version=version,
      description="mcviz",
      long_description=dedent("""
          `MCViz` is intended to be a tool for novices to have a quick play 
          around in, or for more serious users and people who need to explore 
          generator information to make sense of what is going on.
      """).strip(),      
      classifiers=[
        'Development Status :: 1 - Alpha',
        'Intended Audience :: Physicists :: Developers',
        'GNU Affero General Public License v3',
      ],
      keywords='mcviz hep montecarlo hepmc graphviz svg visualization',
      author='Johannes Ebke, Peter Waller and Tim Brooks (see AUTHORS)',
      author_email='dev@mcviz.net',
      url='http://mcviz.net',
      license='Affero GPLv3',
      packages=find_packages(),
      entry_points={"console_scripts" : ["mcviz = mcviz:main"]},
      package_data={
        "mcviz" : ["VERSION"],
        "mcviz.utils.svg" : ["ParticleData.xml", "texglyph.cache"],
        "mcviz.utils.svg.data" : ["*.js", "*.xml"],
      },
      install_requires=[
        'argparse',
      ],
      )

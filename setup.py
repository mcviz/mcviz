from setuptools import setup, find_packages
from textwrap import dedent

version = "2014.12.21"

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
      author='Johannes Ebke and Peter Waller',
      author_email='dev@mcviz.net',
      url='http://mcviz.net',
      license='Affero GPLv3',
      packages=find_packages(),
      entry_points={"console_scripts" : ["mcviz = mcviz:main"]},
      package_data={
        "mcviz.utils.svg.data" : ["*.js", "*.xml","ParticleData.xml", "texglyph.cache"]
      },
      install_requires=[
        'argparse',
      ],
      )

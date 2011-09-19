CODE=mcviz/*.py Makefile bin/*.py

pyclean:
	find . -iname "*.pyc" -exec rm {} \;

mcviz/VERSION: .git/
	git describe --tags > mcviz/VERSION

dist: pyclean mcviz/VERSION

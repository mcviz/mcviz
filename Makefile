CODE=mcviz/*.py Makefile bin/*.py

EXTRAOPTS=-I -c kinks -c gluballs

pyclean:
	find . -iname "*.pyc" -exec rm {} \;

inputs/pythia01.referencedot: inputs/pythia01.out 
	time python2.6 bin/mcviz.py ${EXTRAOPTS} $< > $@

inputs/pythia01.testdot: inputs/pythia01.out ${CODE}
	time python2.6 bin/mcviz.py ${EXTRAOPTS} $< > $@

checkout_references:
	git checkout uptodate_references inputs/pythia01.referencedot

check: checkout_references inputs/pythia01.testdot
	diff -u inputs/pythia01.referencedot inputs/pythia01.testdot | less -F
	rm inputs/pythia01.testdot
	git reset -q HEAD inputs/pythia01.referencedot
	git checkout inputs/pythia01.referencedot


CODE=mcviz/*.py Makefile bin/*.py

EXTRAOPTS=-I -c kinks -c gluballs

pyclean:
	find . -iname "*.pyc" -exec rm {} \;

all: inputs/pythia01.ps

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

%.dot: %.out ${CODE}
	time python2.6 bin/mcviz.py -c kinks $< > $@

%.ps: %.dot
	time fdp -Tps -o $@ $<$< 2> /dev/null

%.tex: %.dot
	time dot2tex -s -c -t raw --prog fdp $< > $@

%.pdf: %.tex
	time pdflatex -output-directory $(dir $@) $<

%.png: %.dot
	time fdp -Tpng -o $@ $< 2> /dev/null

%.svg: %.dot
	time fdp -Tsvg -o $@ $< 2> /dev/null
	
%.sfdpsvg: %.dot
	time fdp -Tsvg -o $@ $< 2> /dev/null

%.dotsvg: %.dot
	time dot -Tsvg -o $@ $< 2> /dev/null
	
%.dotpng: %.dot
	time dot -Tpng -o $@ $< 2> /dev/null

test:
	nosetests tests/



# Does not work :-(
	
#find . -iname "*.py" | xargs grep TODO
#if $? == 0
#    echo "WARNING: TODOs remain"
#endif


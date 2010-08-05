CODE=MCViz/*.py Makefile bin/*.py

EXTRAOPTS=-c kinks -c gluballs

all: inputs/pythia01.ps

inputs/pythia01.referencedot inputs/pythia01.testdot: inputs/pythia01.out
	time python2.6 bin/mcviz.py ${EXTRAOPTS} $< > $@

check: inputs/pythia01.referencedot inputs/pythia01.testdot
	diff -u inputs/pythia01.referencedot inputs/pythia01.testdot | less
	rm inputs/pythia01.testdot

%.dot: %.out ${CODE}
	time python2.6 bin/mcviz.py -c kinks $< > $@

%.ps: %.dot
	time fdp -Tps -o $@ $<

%.tex: %.dot
	time dot2tex -s -c -t raw --prog fdp $< > $@

%.pdf: %.tex
	time pdflatex -output-directory $(dir $@) $<

%.png: %.dot
	time fdp -Tpng -o $@ $<

%.svg: %.dot
	time fdp -Tsvg -o $@ $<
	
%.sfdpsvg: %.dot
	time fdp -Tsvg -o $@ $<

%.dotsvg: %.dot
	time dot -Tsvg -o $@ $<
	
%.dotpng: %.dot
	time dot -Tpng -o $@ $<

test:
	nosetests tests/



# Does not work :-(
	
#find . -iname "*.py" | xargs grep TODO
#if $? == 0
#    echo "WARNING: TODOs remain"
#endif


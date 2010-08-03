CODE=MCViz/*.py Makefile bin/*.py

all: inputs/pythia01.ps

%.dot: %.out ${CODE}
	time python2.6 bin/mcviz.py -c kinks $< > $@

%.ps: %.dot
	time fdp -Tps -o $@ $<

%.tex: %.dot
	time dot2tex -s -c -t raw --prog fdp $< > $@

%.pdf: %.tex
	time pdflatex $<

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


.PRECIOUS: %.dot

all: inputs/pythia01.ps

%.dot: %.out MCViz/MCGraph.py
	time python2.6 bin/mcviz.py -c gluballs -c kinks $< > $@

%.ps: %.dot
	time fdp -Tps -o $@ $<

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


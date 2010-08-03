.PRECIOUS: %.dot

all: inputs/pythia01.ps

%.dot: %.out MCViz/MCGraph.py
	time python2.6 bin/mcviz.py $< > $@

%.ps: %.dot
	time fdp -Tps -o $@ $<

%.png: %.dot
	time fdp -Tpng -o $@ $<

test:
	nosetests tests/



# Does not work :-(
	
#find . -iname "*.py" | xargs grep TODO
#if $? == 0
#    echo "WARNING: TODOs remain"
#endif


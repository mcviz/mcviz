

all: inputs/pythia01.ps

%.dot: %.out MCViz/MCGraph.py
	time python2.6 MCViz/MCGraph.py $< > $@

%.ps: %.dot
	time fdp -Tps -o $@ $<

%.png: %.dot
	time fdp -Tpng -o $@ $<



all: inputs/pythia01.ps

%.dot: %.out
	time python2.6 MCViz/MCGraph.py $^ > $@

%.ps: %.dot
	fdp -Tps -o $@

%.png: %.dot
	fdp -Tpng -o $@


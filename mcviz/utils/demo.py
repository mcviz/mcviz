from os.path import basename, exists

from mcviz import main
from logger import get_logger, log_level; log = get_logger("mcviz.demo")

DEMOS = []
define_demo = DEMOS.append

# Not yet ready for primetime
SKIP = set(("Pluck", "Unsummarize", "Phi"))

def generate_simple(input_file, toolarg, tools):
    for tool in sorted(tools):
        if tool in SKIP: 
            continue
        args = basename(input_file), toolarg.lstrip("--"), tool
        output_file = "mcv-demo-%s-%s-%s.svg" % args
        if exists(output_file):
            continue
        from sys import argv
        args = [argv[0], "--quiet", input_file, toolarg, tool, "--output", output_file]
        #print args
        log.info("Running 'mcviz %s'", " ".join(args[1:]))
        try:
            main(args)
        except KeyboardInterrupt, SystemExit:
            raise
        except Exception:
            log.exception("Caught an exception whilst generating demos")
            log.error("Skipping subsequent tools (%s) for this file." % toolarg)
            break
            

@define_demo
def gen_simple_tools(input_file):
    from mcviz.tools import tools
    generate_simple(input_file, "--tool", sorted(tools))

@define_demo
def gen_simple_layouts(input_file):
    from mcviz.layouts import layouts
    generate_simple(input_file, "--layout", sorted(layouts))
 
@define_demo       
def gen_simple_styles(input_file):
    from mcviz.styles import styles
    generate_simple(input_file, "--style", sorted(styles))

def run_demo(input_file):
    """
    Run all demos in turn
    """
    from logging import WARNING
    with log_level(WARNING):
        for demo in DEMOS:
            demo(input_file)

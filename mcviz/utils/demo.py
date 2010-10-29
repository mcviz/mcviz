from os.path import basename, exists
from sys import argv

from logging import getLogger; log = getLogger("mcviz.demo")

from mcviz import main
from logger import log_level

class SkipFile(Exception): pass

DEMOS = []
define_demo = DEMOS.append

# Not yet ready for primetime
SKIP = set(("Pluck", "Unsummarize", "Phi"))

def go(output_file, *args):
    if exists(output_file):
        log.verbose("  Skipping %s since it already exists", output_file)
        return False
        
    log.info("  Running 'mcviz %s'", " ".join(args))
    try:
        main([argv[0], "--quiet", "--output", output_file] + list(args))
        return True
    except KeyboardInterrupt, SystemExit:
        raise
    except Exception:
        log.exception("Caught an exception whilst generating demos")
        raise SkipFile

def generate_simple(input_file, toolarg, tools):
    for tool in sorted(tools):
        strargs = basename(input_file), toolarg.lstrip("--"), tool
        output_file = "mcv-demo-%s-%s-%s.svg" % strargs
        
        if tool in SKIP:
            continue
        
        try:
            go(output_file, input_file, toolarg, tool)
        except SkipFile:
            break

def generate_multitool(input_file, *args):
    from re import sub
    namefragment = sub("-.", "_", "".join(args)).lstrip("_")
    strargs = basename(input_file), namefragment
    output_file = "mcv-demo-%s-MT-%s.svg" % strargs
    try:
        go(output_file, input_file, "--resolution=1024x768", "-F", *args)
    except SkipFile: pass

@define_demo
def contract_kink_gluball_jet_style_color_fixhad(input_file):
    generate_multitool(input_file, 
        "-tKinks", "-tClusters", "-tGluballs", "-tLoops",
        "-lFixHad",
        "-sColor"
    )

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
    log.info("Processing %s" % input_file)
    for demo in DEMOS:
        demo(input_file)

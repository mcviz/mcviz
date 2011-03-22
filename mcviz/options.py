from __future__ import division

from optparse import OptionParser, OptionGroup
import sys

from mcviz import FatalError
from mcviz.tools import tool_type_options
from mcviz.tools.tools import tool_types, tool_classes

def get_option_parser():
    usage = "usage: %prog [options] {hepmc_file|pythia_log}"

    p = OptionParser(usage=usage, add_help_option=False)
    o = p.add_option
    #
    # Program control
    #
    tool_type_opts = tool_type_options()
    help_topics = ["all"] + [l.strip("-").replace("--","_") for s, l, h in tool_type_opts]
    o("-h", "--help", action="store_true", help="show help. You can specify one of the following topics: %s" % ", ".join(help_topics))

    o("-q", "--quiet", action="store_true", help="Do not print out anything except warnings and errors")

    o("-v", "--verbose", action="count", help="Be more verbose. Specify -vv for debug output")

    o("--demo", action="store_true", 
      help="Create many demo svgs in the current directory (takes a while)")

    g = OptionGroup(p, "The MCViz Toolbox", "")
    p.add_option_group(g)
    o = g.add_option

    for shortopt, longopt, helptext in tool_type_opts:
        o(shortopt, longopt, action="append", default=[], help=helptext)

    o("", "--optionset", action="append", default=["cl"], help="Select a set of default settings to use. Currently only 'cl'")

    g = OptionGroup(p, "Debug", "These options may help in finding problems")
    p.add_option_group(g)
    o = g.add_option

    o("-d", "--debug", action="store_true",
      help="Drop to ipython shell on exception")
    
    o("--profile", action="store_true", 
      help="Turn on profiling (requires bootstrap_extenv to have been run)")

    o("--dump-dot", action="store_true",
      help="Print the DOT data passed into graphviz.")
    return p
    
def parse_options(argv=sys.argv):
    parser = get_option_parser()
    options, args = parser.parse_args(argv)
    if options.help:
        if len(args) == 1:
            parser.print_help()
            print("")
            print("To show extensive help, type %s --help all" % args[0])
            print("For a list of examples, type %s --help examples" % args[0])
        elif args[1] == "examples":
            print("Sorry, Peter is still working on them!")
        else:
            topic = args[1]
            tool_type_opts = tool_type_options()
            help_topics = ["all"] + [l.strip("-").replace("--","_") for s, l, h in tool_type_opts]
            if not topic in help_topics:
                print "Unknown help topic '%s'. Known topics: %s" % (topic, ", ".join(help_topics))
                sys.exit(-1)
            for name, cls in tool_types.iteritems():
                if topic == "all" or topic == name:
                    print("")
                    print("'%s': %s" % (name, cls._short_help))
                    if cls._merge_classes:
                        helptext2 = "All tools of the type '%s' are merged into one class. "\
                                "There are 'base' classes (one of which must be included) and supplementary classes." % name
                    else:
                        helptext2 = "Tools of type '%s' are simple tools, and can be applied several times (if sensible)" % name 
                    print("%s" % (helptext2))
                    print("Here is a list of all %ss with their arguments. Arguments are separated by colons ':'." % (name))
                    print("Arguments can be positional or specified by name. Example: -e dot:True:orientation=LR")

                    # % (cls._type, cls._short_opt, cls._merge_classes))
                    for tname, cls in tool_classes[name].iteritems():
                        helptext1 = cls._help if hasattr(cls, "_help") else ""
                        print("  * %s%s: %s" % (cls._name, " (base)" if (hasattr(cls, "_base") and cls._base) else "", helptext1))

                        if cls.global_args():
                             print("      This %s uses the global arguments %s" % (name, ", ".join(cls.global_args())))
                        if cls.args():
                             for arg in cls.args():
                                 arg_name, arg_obj = arg
                                 # default doc choices
                                 choices = "(choices: %s)" % ", ".join("'%s'" % c for c in arg_obj.choices) if arg_obj.choices else ""
                                 print("        - %s='%s': %s %s" % (arg_name, arg_obj.default, arg_obj.doc, choices))

                                 
        sys.exit(0)
    return options, args

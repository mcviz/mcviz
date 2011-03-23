from __future__ import division

from optparse import OptionParser, OptionGroup, SUPPRESS_HELP
import sys

from mcviz import FatalError
from mcviz.tools import tool_type_options
from mcviz.tools.tools import tool_types, tool_classes

help_topics = ["all", "examples"] + tool_types.keys()

def get_option_parser():
    usage = "usage: %prog [options] {hepmc_file|pythia_log}"

    p = OptionParser(usage=usage, add_help_option=False)
    o = p.add_option
    #
    # Program control
    #
    o("-h", "--help", action="store_true", help="Show help. You can specify one of the following topics: %s. You can also specify the name of any tool." % ", ".join(help_topics))

    o("-q", "--quiet", action="store_true", help="Do not print out anything except warnings and errors")

    o("-v", "--verbose", action="count", help="Be more verbose. Specify -vv for debug output")

    o("--demo", action="store_true", 
      help="Use pretty looking default (equivalent to --optionset=demo)")

    g = OptionGroup(p, "The MCViz Toolbox", "")
    p.add_option_group(g)
    o = g.add_option

    for shortopt, longopt, helptext in tool_type_options():
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

    o("--links", action="store_true", help=SUPPRESS_HELP)
    return p

def print_type_help(cls, links=False):
    name = cls._type
    text = []
    text.append("## %s\n%s\n" % (name, cls._short_help))
    if cls._merge_classes:
        helptext2 = "All tools of the type '%s' are merged into one class. "\
                "There are 'base' classes (one of which must be included) and supplementary classes." % name
    else:
        helptext2 = "Tools of type '%s' are simple tools, and can be applied several times (if sensible)" % name 
    text.append("%s" % (helptext2))

    # The following is an automatic example generator. It avoids using "None" and "" arguments if it can help it
    def nonnull(args):
        return [a for a in args if not a[1].default in [None, ""]]
    tool = max((len(nonnull(t.args())), len(t.args()), t) for t in reversed(tool_classes[name].values()))[2]
    arglist = (nonnull(tool.args()) + tool.args())
    n_nonnull = len(nonnull(tool.args()))
    if len(arglist) == 0:
        pass # no arguments 
    elif n_nonnull == 1 or (n_nonnull == 0 and len(arglist) == 1):
        argname, argcls = arglist[0]
        example = "--%s %s:%s or --%s %s:%s=%s" % (cls._type, tool._name, argcls.default, cls._type, tool._name, argname, argcls.default)
        text.append("This is a list of all %ss with their arguments. Arguments are separated by colons ':'." % (name))
        text.append("Arguments can be positional or specified by name.")
        text.append("")
        text.append("Example: %s" % (example))
    else:
        text.append("Here is a list of all %ss with their arguments. Arguments are separated by colons ':'." % (name))
        (arg1name, arg1cls), (arg2name, arg2cls) = arglist[:2]
        example = "--%s %s:%s:%s=%s" % (cls._type, tool._name, arg1cls.default, arg2name, arg2cls.default)
        text.append("Arguments can be positional or specified by name.")
        text.append("")
        text.append("Example: %s" % example)
    text.append("")

    # Print the help for all the subtools
    for tool in tool_classes[name].values():
        text.extend(print_tool_help(" "*6, tool, links))
    return text

def print_tool_help(indent, tool, links=False):
    text = []
    helptext = (": " + tool.__doc__) if tool.__doc__ else ""
    if links:
        helptext += "\n![example image](%s_%s.png)" % (tool._type.lower(), tool._name.lower())
    base_str = " (base)" if (hasattr(tool, "_base") and tool._base) else ""
    text.append("  * %s%s%s" % (tool._name, base_str, helptext))


    if tool.global_args():
         text.append("%sThis %s uses the options %s" % (indent, tool._type, ", ".join(tool.global_args())))
    if tool.args():
         for arg in tool.args():
             arg_name, arg_obj = arg
             # default doc choices
             choices = "(choices: %s)" % ", ".join("'%s'" % c for c in arg_obj.choices) if arg_obj.choices else ""
             text.append("%s * %s='%s': %s %s" % (indent, arg_name, arg_obj.default, arg_obj.doc, choices))
    return text
    
def parse_options(argv=sys.argv):
    parser = get_option_parser()
    options, args = parser.parse_args(argv)

    if options.demo:
        options.optionset = ["demo"]

    if options.help:
        # construct a list of tools
        tool_list = reduce(list.__add__, (tc.values() for tc in tool_classes.values()))
        tool_map = dict((t._name.lower(), t) for t in tool_list)
        tool_types_lower = dict((tn.lower(), ty) for tn, ty in tool_types.iteritems())


        if len(args) == 1:
            parser.print_help()
            print("")
            print("To show extensive help, type %s --help all" % args[0])
            print("For a list of examples, type %s --help examples" % args[0])
            sys.exit(0)
        
        topic = args[1].lower()
        if topic == "examples":
            text = ["Sorry, Peter is still working on them!"]
        elif topic == "all":
            text = []
            for cls in tool_types.itervalues():
                text.extend(print_type_help(cls, options.links))
                text.append("")
        elif topic in tool_types_lower:
            text = print_type_help(tool_types_lower[topic], options.links)
        elif topic in tool_map:
            text = print_tool_help(" "*4, tool_map[topic], options.links)
        else:
            print "Unknown help topic '%s'. Known topics: %s (and all tool names)" % (topic, help_topics)
            sys.exit(-1)
        print("\n".join(text))
        sys.exit(0)
    return options, args

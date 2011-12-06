from os.path import dirname
from textwrap import dedent

import mcviz
from . import log; log = log.getChild("help")
from .tools.tools import tool_types, tool_classes

help_topics = ["all", "examples"] + tool_types.keys()

GIT_URL = "https://github.com/mcviz/mcviz/tree/master/mcviz"


def print_type_help(cls, links=False):
    name = cls._type
    text = []
    text.append("## {0:s}\n{1:s}\n".format(name, cls._short_help))
    if cls._merge_classes:
        helptext2 = "All tools of the type '{0:s}' are merged into one class. "\
                "There are 'base' classes (one of which must be included) and supplementary classes."\
                .format(name)
    else:
        helptext2 = "Tools of type '{0}' are simple tools, and can be applied several times (if sensible)".format(name)
    text.append(str(helptext2))

    # The following is an automatic example generator. It avoids using "None" and "" arguments if it can help it
    def nonnull(args):
        return [a for a in args if not a[1].default in [None, ""]]
        
    documented_classes = [v for v in tool_classes[name].values() if v.__doc__ is None or not "UNDOCUMENTED" in v.__doc__]
    sortable_classes = ((len(nonnull(t.args())), len(t.args()), t) for t in reversed(documented_classes))
    tool = max(sortable_classes)[2]
    arglist = (nonnull(tool.args()) + tool.args())
    n_nonnull = len(nonnull(tool.args()))
    
    if len(arglist) == 0:
        pass # no arguments 
        
    elif n_nonnull == 1 or (n_nonnull == 0 and len(arglist) == 1):
        argname, argcls = arglist[0]
        example = "--{0} {1}:{2} or --{3} {4}:{5}={6}"\
            .format(cls._type, tool._name, argcls.default, cls._type, tool._name, argname, argcls.default)
        text.append("This is a list of all {0}s with their arguments. Arguments are separated by colons ':'.".format(name))
        text.append("Arguments can be positional or specified by name.")
        text.append("")
        text.append("Example: {0}".format(example))
        
    else:
        text.append("Here is a list of all {0}s with their arguments. Arguments are separated by colons ':'.".format(name))
        (arg1name, arg1cls), (arg2name, arg2cls) = arglist[:2]
        example = "--{0} {1}:{2}:{3}={4}".format(cls._type, tool._name, arg1cls.default, arg2name, arg2cls.default)
        text.append("Arguments can be positional or specified by name.")
        text.append("")
        text.append("Example: {0}".format(example))
        
    text.append("")

    # Print the help for all the subtools
    for toolname, tool in sorted(tool_classes[name].iteritems()):
        text.extend(print_tool_help(" "*6, tool, links) + [""])
    
    return text

def print_tool_help(indent, tool, links=False):
    if tool.__doc__ and "UNDOCUMENTED" in tool.__doc__:
        return []
        
    text = []

    helptext = dedent(tool.__doc__).strip() if tool.__doc__ else ""
    helptext = "\n    ".join(helptext.split("\n"))
    
    if links:
        helptext += "\n![example image]({0}_{1}.png)".format(tool._type.lower(), tool._name.lower())
    
    from inspect import getfile
    
    definition = getfile(tool)[len(dirname(getfile(mcviz.main))):].rstrip("co")
    
    base_str = " (base)" if (hasattr(tool, "_base") and tool._base) else ""
    text.append(("  * **{0}**{1}:\n"
                 "    [{2}]({GIT_URL}{2})\n"
                 "    {3}").format(tool._name, base_str, definition, helptext, 
                                   GIT_URL=GIT_URL))

    if tool.global_args():
         text.append("{0}This {1} uses the options {2}"
             .format(indent, tool._type, ", ".join(tool.global_args())))
             
    if tool.args():
         for arg in tool.args():
             arg_name, arg_obj = arg
             # default doc choices
             if arg_obj.choices is None:
                 choices = ""
             else:
                 choices = " (choices: {0})".format(", ".join("'{0}'".format(c) for c in arg_obj.choices))
             text.append("{0} * {1}='{2}': {3}{4}".format(indent, arg_name, arg_obj.default, arg_obj.doc, choices))
             
    return text
    
def did_you_mean(topic, available):
    from difflib import get_close_matches
    close = get_close_matches(topic, available)
    
    if close:
        bits = ", ".join(sorted(close))
        left, lastcomma, right = bits.rpartition(", ")
        if lastcomma:
            bits = "{0} or {1}".format(left, right)
        log.error("Did you mean {0}?".format(bits))
        
        if len(close) == 1:
            return close[0]
    
def run_help(parser, args):

    # construct a list of tools
    tool_list = reduce(list.__add__, (tc.values() for tc in tool_classes.values()))
    tool_types_lower = dict((tn.lower(), ty) for tn, ty in tool_types.iteritems())
    
    tool_map = {}
    for t in tool_list:
        tool_map.setdefault(t._name.lower(), []).append(t)

    if not args.filename:
        parser.print_help()
#        print("")
#        print("To show extensive help, type %(prog)s --help all")
#        print("For a list of examples, type %(prog)s --help examples")
        return -1
    
    topic = args.filename.lower()
    
    if topic.rstrip("s") in tool_types_lower:
        # If the non-plural version exists, lookup that
        topic = topic.rstrip("s")
    
    if topic == "examples":
        text = ["Sorry, Peter is still working on them!"]
        
    elif topic == "all":
        text = []
        for cls in tool_types.itervalues():
            text.extend(print_type_help(cls, args.links))
            text.append("")
            
    elif topic in tool_types_lower:
        text = print_type_help(tool_types_lower[topic], args.links)
        
    elif topic in tool_map:
        tools = tool_map[topic]
        text = []
        for tool in tools:
            text.append("--{type} / -{shortopt}:"
                        .format(type=tool._type, shortopt=tool._short_opt))
            text.extend(print_tool_help(" "*4, tool, args.links) + [""])
        
    else:
        print "Unknown help topic '{0}'. Known topics: {1} (and all tool names)".format(topic, help_topics)
        did_you_mean(topic, help_topics + sorted(tool_map))
        return -1
        
    print("\n".join(text))
    
    return 0

from .. import log; log = log.getChild(__name__)

import re

from new import classobj
from os import isatty
from sys import stdin


tool_types = {}
tool_classes = {}

class ArgParseError(Exception):
    pass

class ToolSetting(object):
    def __init__(self, name, *args, **kwargs):
        self.name = name
        self.args = args
        self.kwargs = kwargs

    @classmethod
    def from_string(self, in_string):
        keyword_args = {}
        positional_args = []

        ts_split = re.split(r"(?<!\\)\:", in_string)
        tool_name, args = ts_split[0], ts_split[1:]

        for arg in args:
            # Try to find an unescaped equal sign
            tp = re.split(r"(?<!\\)\=", arg)
            if len(tp) == 2:
                arg, val = tp
                keyword_args[arg] = val
            elif not arg.strip():
                pass
            elif len(tp) == 1:
                positional_args.append(arg)
            else:
                raise ToolParseError(self, "too many '=' in %s" % arg)

        return ToolSetting(tool_name, *positional_args, **keyword_args)

    @classmethod
    def settings_from_options(cls, options):
        res = {}
        for tool_type in sorted(tool_types.keys()):
            tool_strings = getattr(options, tool_type.replace("-","_"))
            res[tool_type] = map(cls.from_string, tool_strings)
        return res
        
    def get_class(self, tool_type):
        class_args = []
        if not self.name in tool_classes[tool_type]:
            possible = tool_classes[tool_type].keys()
            log.error("No such {0} tool {1}".format(tool_type, self.name))
            
            found = False
            from ..help import did_you_mean
            meant = did_you_mean(self.name, possible)
            if meant and isatty(stdin.fileno()):
                try:
                    yes = raw_input("[Y/n] ").lower() in ("y", "")
                    if yes:
                        log.debug("Rewriting tool '{0}' to '{1}'".format(self.name, meant))
                        self.name, found = meant, True
                except (IOError, EOFError):
                    pass
            
            if not found:
                choices = ", ".join(possible)
                raise ArgParseError(
                    "no such {0}: {1}\npossible choices are: {2}"
                    .format(tool_type, self.name, choices))
        return tool_classes[tool_type][self.name]


class ToolParseError(ArgParseError):
    def __init__(self, tool, msg, exc = None):
        self.tool = tool
        self.original_exception = exc
        new_msg = "%s %s: %s" % (tool._type, tool._name, msg)
        super(ToolParseError, self).__init__(new_msg)

class Arg(object):
    def __init__(self, name, converter, doc, default=None, choices=None, web=False):
        """<converter> can be float, int, str, or even a function
        WARNING: Any function put in here will receive a user input string
        and must treat the string as TAINTED"""
        self.name = name
        self.converter = converter
        self.doc = doc
        self.default = default
        self.choices = choices
        self.web = web

    def convert(self, in_string, tool):
        try:
            return self.converter(in_string)
        except Exception, x:
            raise ToolParseError(tool, "cannot convert '%s' to %s for argument '%s'" % (in_string, self.converter, self.name) )

    @classmethod
    def bool(cls, s):
        if s.lower() in ("true", "1", "wahr", "yes"):
            return True
        elif s.lower() in ("false", "0", "falsch", "no"):
            return False
        else:
            raise Exception("Unknown bool value!")


def tool_type_options():
    res = []
    for tool_type in sorted(tool_types.keys()):
        cls = tool_types[tool_type]
        tlist = sorted(tool_classes[tool_type].keys())
        helptext = "%s (%s)" % (cls._short_help, ", ".join(tlist))
        if cls._short_opt:
            res.append(("-%s" % cls._short_opt, "--%s" % cls._type, helptext))
    return res

def debug_tools():
    for name, cls in tool_types.iteritems():
        log.debug("Tool-Type '%s'; short option: %s; merge: %s"
            % (cls._type, cls._short_opt, cls._merge_classes))
        for tname, cls in tool_classes[name].iteritems():
            log.debug(" %s '%s'" % (cls._type, name))
            log.debug("   using global arguments: %s" % str(cls.global_args()))
            log.debug("   local arguments: %s" % str(cls.args()))

class ToolCreator(type):
    def __new__(cls, name, baseClasses, classdict):
        ncls = type.__new__(cls, name, baseClasses, classdict)
        if "_type" in classdict:
            tool_classes.setdefault(ncls._type, {})
            tool_types[ncls._type] = ncls
        elif "_base" in classdict:
            pass
        elif hasattr(ncls, "_type"):
            tool_name = classdict.get("_name", name)
            tool_classes.setdefault(ncls._type, {})[tool_name] = ncls
        elif not "__metaclass__" in classdict:
            # only "Tool" is allowed to have no _type
            print "WARNING: Found Tool without type: %s" % name
        if not hasattr(ncls, "_name"):
            ncls._name = name
        return ncls

class Tool(object):
    __metaclass__ = ToolCreator

    """Name of this tool"""
    #_name = "Empty"

    """list of Arguments to this tool (Arg class)"""
    _args = ()

    """list of (string) global arguments which are used - they are copied into options"""
    _global_args = ()

    """Set to true for example in Layout; if the classes should be merged
    and one tool created instead of instantiating every class.
    You need one FundamentalTool in the list!"""
    _merge_classes = False


    def __init__(self, settings=None):
        # Primary default for all options is None
        args = self.args()
        self.options = dict(((name, arg.default) for name, arg in args))
        if settings:
            self.apply_settings(settings)

    @classmethod
    def args(cls):
        args_names = []
        args_list = []
        for base_class in reversed(cls.mro()):
            if hasattr(base_class, "_args"):
                for arg in base_class._args:
                    if not arg.name in args_names:
                        args_names.append(arg.name)
                        args_list.append(arg)
        return zip(args_names, args_list)

    @classmethod
    def decorate(cls, name, title=None, args=None):
        if title is None:
            title = name
        if args is None:
            args = ()
        def decorated(func):
            def tool_specific(self, *pargs):
                return func(*pargs, **self.options)
            clsd = dict(_args=args, _name=title, __call__=tool_specific, 
                        __doc__=func.__doc__, __module__=func.__module__)
            return classobj(name, (cls,), clsd)
        return decorated

    @classmethod
    def global_args(cls):
        args = set()
        for base_class in cls.mro():
            if hasattr(base_class, "_global_args"):
                args.update(base_class._global_args)
        return args

    @classmethod
    def build_tools(cls, tool_type, settings, global_args):
        type_cls = tool_types[tool_type]
        classes = [s.get_class(tool_type) for s in settings]
        if type_cls._merge_classes:
            specific_class = cls.create_specific_class(tool_type, classes)
            tool = specific_class()
            tool.read_global_args(global_args)
            for s in settings:
                tool.read_settings(s)
            tools = [tool]
        else:
            tools = []
            for setting in settings:
                tool = setting.get_class(tool_type)()
                tool.read_global_args(global_args)
                tool.read_settings(setting)
                tools.append(tool)
        return tools

    @classmethod
    def create_specific_class(cls, tool_type, classes):
        """
        Compose a new layout from other layouts. This is tricky because we 
        dynamically create a new layout class out of objects passed on the 
        commandline. This means that the commandline must follow Python's 
        inheritance rules. Not ideal, but convenient for the moment.
        """
        bases = tuple(reversed(classes))
        n_fundamental = len([1 for b in bases if issubclass(b, FundamentalTool)])
        if n_fundamental != 1:
            # We didn't include a fundamental layout or have more than one!
            blist= ", ".join(tc._name for tc in tool_classes[tool_type].values()
                             if issubclass(tc, FundamentalTool))
            if n_fundamental == 0:
                msg = ("You tried to construct a combination of {type}s "
                       "without including one of the base {type}s. Please "
                       "use at least one of the following {type}s: {blist}"
                       "".format(type=tool_type, blist=blist))
            else:
                msg = ("You tried to construct a combination of {type}s "
                       "with more than one base {type}s. "
                       "Please use only one of these {type}s: "
                       "{blist}".format(type=tool_type, blist=blist))

            raise ArgParseError(msg)
        
        classname = "%s_specific" % tool_type
        log.debug("Creating %s with bases %r", classname, bases)
        return classobj(classname, bases, {})

    def read_global_args(self, global_args):
        for arg in self.global_args():
            self.options[arg] = getattr(global_args, arg)

    def read_settings(self, setting):
        my_args = self.args()
        my_args_dict = dict(my_args)

        keyword_args = {}
        positional_args = []

        for arg, val in setting.kwargs.iteritems():
            if not arg in my_args_dict:
                raise ToolParseError(self, "unknown argument '%s'" % arg)
            keyword_args[arg] = my_args_dict[arg].convert(val, self)
            print arg, "=", my_args_dict[arg].convert(val, self)


        if len(setting.args) > len(my_args):
            raise ToolParseError(self, "too many arguments!")

        positional_arg_d = {}
        for (n, arg), in_string in zip(my_args, setting.args):
            positional_arg_d[n] = arg.convert(in_string, self)

        for arg in keyword_args:
            if arg in positional_arg_d:
                raise ToolParseError(self, "argument '%s' specified as both "
                                     "positional and keyword argument" % arg)

        self.options.update(keyword_args)
        self.options.update(positional_arg_d)

        for arg, val in self.options.iteritems():
            if arg in my_args_dict and my_args_dict[arg].choices:
                if not val in my_args_dict[arg].choices:
                    raise ToolParseError(self, "invalid choice '%s' (%s)" 
                                % (val, ", ".join(my_args_dict[arg].choices)))

        log.debug("%s %s options after local args: %s" % (self._type, self._name, self.options))

class FundamentalTool(object):
    """
    Needed for tool types which merge classes. 
    At least one class must have this.
    """

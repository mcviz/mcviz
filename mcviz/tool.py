import re

class ArgParseError(Exception):
    pass

class ToolParseError(ArgParseError):
    def __init__(self, tool, msg, exc = None):
        self.tool = tool
        self.original_exception = exc
        new_msg = "%s %s: %s" % (tool.tool_type, tool.tool_name, msg)
        super(ToolParseError, self).__init__(new_msg)

class Tool(object):

    """list of (<argument_name>, <converter>) tuples
       <converter> can be float, int, str, or even a function
       WARNING: Any function put in here will receive a user input string
       and must treat the string as TAINTED"""
    _args = ()

    """list of global arguments which are used - they are copied into options"""
    _global_args = ()

    """Dictionary of arguments to default values, both local and global"""
    _default = None

    """Dictionary mapping local arguments to lists of choices"""
    _choices = None

    def __init__(self, tool_type, tool_name):
        self.tool_name = tool_name
        self.tool_type = tool_type

    def test_assertions(self):
        arg_converters = dict(self._args)
        for arg in self._defaults:
            assert arg in self._args
        for arg in self._choices:
            assert arg in self._args

    def read_options(self, args, global_args):
        positional_args = []
        keyword_args = {}

        arg_converters = dict(self._args)
        arg_list = arg_converters.keys()
    
        # Primary default for all options is None
        self.options = dict(zip(arg_list, [None]*len(arg_list)))
        # Update with the specified defaults
        self.options.update(self._default)
        # Use any global args that are specified
        for arg in self._global_args:
            if not hasattr(global_arg, arg):
                raise ToolParseError(self, "unknown global argument '%s'" % arg)
            self.options[arg] = getattr(global_args, arg)
        # Now update with local options
        for arg in args:
            # Try to find an unescaped equal sign
            tp = re.split(r"(?<!\\)\=", arg)
            if len(tp) == 2:
                arg, val = tp
                if not arg in arg_converters:
                    raise ToolParseError(self, "unknown argument '%s'" % arg)
                
                if arg in self._choices and not val in self._choices[arg]:
                    raise ToolParseError(self, "invalid choice '%s' (%s)" 
                                    % (val, ", ".join(self._choices[arg])))

                converter = arg_converters[arg]
                try:
                    cval = converter(val)
                except Exception, x:
                    raise ToolParseError(self, "cannot convert '%s'" % val)

                keyword_args[arg] = cval
            elif len(tp) == 1:
                positional_args.append(arg)
            else:
                raise ToolParseError(self, "too many '=' in %s" % arg)

        if len(positional_args) > len(arg_list):
            raise ToolParseError(self, "too many arguments!")

        positional_args = dict(zip(arg_list, positional_args))
        for arg in keyword_args:
            if arg in positional_args:
                raise ToolParseError(self, "argument '%s' specified as both "
                                     "positional and keyword argument" % arg)

        self.options.update(keyword_args)
        self.options.update(positional_args)




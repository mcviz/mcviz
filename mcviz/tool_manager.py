import re

from .tool import Tool, ArgParseError 
from .transforms import transforms
from .layouts    import layouts
from .styles     import styles
from .painters   import painters
from .utils import timer
from .transforms.tagging import tag

from logging import getLogger; log = getLogger("mcviz.tool_manager")

layout_engines = ["fdp", "neato", "dot", "sfdp", "circo", "twopi"]
annotations = {}

tool_types = ("transform", "layout", "layout-engine", "style", "annotate" , "painter")
tool_dicts = (transforms , layouts , layout_engines , styles , annotations, painters )

tooltypes_dict = dict(zip(tool_types, tool_dicts))

tool_help = {}
tool_help["transform"] = ("Select a transform that is applied to the graph (%s) "
           "Can be applied multiple times." 
            % ", ".join(transforms.keys()))
tool_help["layout"] = ("Select layout classes that are used to layout the graph (%s) "
           "Can also be applied multiple times." 
            % ", ".join(layouts.keys()))
tool_help["layout-engine"] = ("If specified, pipes output through specified "
           "graphviz engine (%s)" 
            % ", ".join(layout_engines))
tool_help["style"] = ("Select styles that are applied to the graph (%s)" 
            % ", ".join(styles.keys()))
tool_help["annotate"] = ("Add an annotation specifying a property to the label "
           "(%s)" 
            % ", ".join(annotations.keys()))
tool_help["painter"] = ("Override autodetect from outputfile extension (%s)" 
            % ", ".join(painters.keys()))

shortcuts = {"transform":"t", "layout":"l", "layout-engine":"e", 
             "style":"s", "annotate":"a" , "painter":"p"}

def tooltype_options():
    return (("-%s" % shortcuts[t], "--%s" % t, tool_help[t]) for t in tool_types)

class ToolManager(object):
    @classmethod
    def from_options(cls, options):
        mgr = cls()
        for tool_type in tool_types:
            for tool_args in getattr(options, tool_type.replace("-","_")):
                mgr.tool_from_string(self, tool_args)
        return mgr

    def __init__(self):
        self.tools = {}
        for tool_type in tool_types:
            self.tools[tool_type] = []

    def tool_from_string(self, tool_type, tool, options):
        tool_dict = tooltypes_dict[tool_type]
        # Regex: Require ":" but without an (unescaped) backslash
        tsplit = re.split(r"(?<!\\)\:", tool_string)

        tool_name, raw_args = tsplit[0], tsplit[1:]

        if not tool_name in tool_dict:
            raise ArgParseError("no such %s: %s\npossible choices are: %s" % 
                    (tool_type, tool_name, tool_dict.keys()))

        tool_class = tool_dict[tool_name]
        tool = tool_class(tool_type, tool_name)
        tool.read_options(raw_args, options)

        self.tools[tool_type].append(tool)
        
    def __getitem__(self, tool_type):
        return self.tools[tool_type]

    def apply(self, tool_type, *args):
        with timer("apply %s" % tool_type, log.VERBOSE):
            for tool in self.tools[tool_type]:
                log.verbose('applying %s: %s' % (tool_type, tool))
                with timer('apply %s' % tool):
                    tool(*args)



        


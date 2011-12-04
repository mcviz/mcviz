from . import log; log = log.getChild(__name__)

from . import Tool, FatalError
from .graph import GraphView
from .tools import ToolSetting, ArgParseError, debug_tools
from .tools.transforms.tagging import tag
from .utils.timer import Timer


class GraphWorkspace(object):

    def __init__(self, name, event_graph, cmdline=""):
        
        self.log = log.getChild(name)
        self.log.debug('Creating new graph workspace {0}'.format(name))
        self.timer = Timer(self.log)
        
        self.name = name
        self.event_graph = event_graph
        self.cmdline = cmdline
                
        self.graph_view = GraphView(event_graph)
        self.layout = None
        self.tools = {}

    def load_tools(self, options):
        debug_tools()
        self.log.debug('Loading tools...')
        with self.timer('load all tools'):
            try:
                settings = ToolSetting.settings_from_options(options)
                self.tools_from_settings(settings, options)
            except ArgParseError, e:
                self.log.fatal("Parse error in arguments: %s" % e.args[0])
                raise FatalError

    def tools_from_settings(self, settings, global_args):
        optionsets = settings.pop("optionset")
        for optionset in Tool.build_tools("optionset", optionsets, global_args):
            optionset(settings)
        for tool_type in settings:
            tools = Tool.build_tools(tool_type, settings[tool_type], global_args)
            self.tools[tool_type] = tools
    
    def apply_tools(self, tool_type, *args):
        tools = self.tools.get(tool_type, ())
        for tool in tools:
            self.log.verbose('applying %s: %s' % (tool_type, tool))
            with self.timer('apply %s' % tool):
                tool(*args)

    def apply_tags(self):
        # Apply all Taggers on the graph
        self.log.debug('tagging graph')
        with self.timer('tag the graph'):
            tag(self.graph_view)

    def clear_tags(self):
        self.log.debug('TODO: remove tags from graph')
    
    def apply_transforms(self):
        self.log.debug("Graph state (before transforms): %s", self.graph_view)
        self.log.verbose("applying transforms")
        with self.timer("apply all transforms", self.log.VERBOSE):
            self.apply_tools("transform", self.graph_view)
        self.log.debug("Graph state (after transforms): %s", self.graph_view)

    def clear_transforms(self):
        self.log.debug('Recreating graph view')
        self.graph_view = GraphView(self.event_graph)

    def apply_annotations(self):
        # Apply any specified annotations onto the layouted graph
        self.log.verbose("applying annotations")
        with self.timer("applied all annotations"):
            self.apply_tools("annotation", self.graph_view)

    def clear_annotations(self):
        self.log.debug('TODO: remove annotations from graph')

    def create_layout(self):
        # Get the specified layout class and create a layout of the graph
        self.log.verbose("applying layout classes")
        with self.timer("layout the graph", self.log.VERBOSE):
            layout, = self.tools["layout"]
            self.layout = layout(self.graph_view)

    def run_layout_engine(self):
        self.log.verbose("running layout engine")
        with self.timer("run layout engine", self.log.VERBOSE):
            self.apply_tools("layout-engine", self.layout)

    def apply_styles(self):
        # Apply any specified styles onto the layouted graph
        self.log.verbose("applying styles")
        with self.timer("applied all styles"):
            self.apply_tools("style", self.layout)

    def clear_styles(self):
        self.log.debug('TODO: remove styles from graph')

    def apply_optionsets(self):
        # Apply any specified styles onto the layouted graph
        self.log.verbose("applying optionsets")
        with self.timer("applied all optionsets"):
            self.apply_tools("optionset", self.tools)

    def paint(self):
        self.log.verbose("painting the graph")
        with self.timer("painted the graph"):
            self.apply_tools("painter", self, self.layout)
       
    def restyle(self):
        self.clear_tags()
        self.clear_styles()
        self.clear_annotations()
        self.apply_tags()
        self.apply_annotations()
        self.apply_styles()

    def run(self):
        self.apply_optionsets()
        self.apply_transforms()
        self.apply_tags()
        self.apply_annotations()
        self.create_layout()
        self.apply_styles()
        self.run_layout_engine()
        self.paint()

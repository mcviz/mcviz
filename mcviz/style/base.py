
class StyleManager(object):
    """
    We need something which can emit CSS classes given a set of styles.
    
    What we want to emit:
    
    <style type="text/css">
        .PythonClassName {
            Properties with the python class
        }
    </style>
    
    <line class="PythonClassName" style="PythonInstanceProperties" />
    """

class Style(object):
    def __init__(self, options):
        self.options = options

class ObjectStyle(object):
    def __init__(self, **kwds):
        self.overrides = kwds

    @classmethod
    def _css_class_text(cls):
        """
        Return the text which needs to go into the <style> tag
        """
        keys = cls.__dict__.keys()
        properties = [k[4:] for k in keys if k.startswith("css_")]
        text = [".%s {" % cls.__name__]
        for k in properties:
            text.append('  %s="%s";' % (k.replace("_", "-"), cls.__dict__[k]))
        text.append("}")
        return "\n".join(text)        
        
    @property
    def _svg_style(self):
        """
        Return the text which this style needs to over-ride for a single instance.
        """
        style = []
        for key, value in self.overrides.iteritems():
            csskey = "css_" + key 
            clsdict = self.__class__.__dict__
            if csskey in clsdict and clsdict[csskey] == value:
                continue
            style.append('%s="%s"' % (key.replace("_", "-"), value))
        return ";".join(style)
class DefaultStyle(Style):
    energy = 0.2
    scale = 0.1
    stroke = "pink"
    fill = "pink"
    stroke_width = 0.05
    
class MyStyle(DefaultStyle):
    pass
    
    

    


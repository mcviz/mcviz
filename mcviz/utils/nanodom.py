
class XMLNode(object):
    def __init__(self, tag, attrs=None, children=None):
        self.tag = tag
        self.attrs = [] if attrs is None else [attrs]
        self.children = [] if children is None else children

    def appendChild(self, child):
        self.children.append(child)

    def setAttribute(self, attr, val):
        self.attrs.append('%s="%s"' % (attr, val))

    def __str__(self):
        open_content = " ".join([self.tag] + self.attrs)
        if not self.children:
            return "<%s />" % open_content
        child_data = "\n".join(unicode(child) for child in self.children)
        open_tag = "<%s>" % open_content
        close_tag = "</%s>" % self.tag
        return "\n".join((open_tag, child_data, close_tag))

class RawNode(XMLNode):
    def __init__(self, data):
        self.data = data

    def __str__(self):
        return self.data
        
    def __unicode__(self):
        return self.data



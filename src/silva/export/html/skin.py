
from five import grok
from silva.core.layout.interfaces import ISilvaLayer


class IHTMLExportLayer(ISilvaLayer):
    """Layer used to export content in HTML.
    """

grok.layer(IHTMLExportLayer)



from five import grok
from silva.core.layout.interfaces import ICustomizableLayer, ISilvaLayer
from zope.publisher.interfaces.browser import IBrowserSkinType


class IHTMLExportLayer(ICustomizableLayer):
    """Layer used to export content in HTML.
    """

class IHTMLExportSkin(IHTMLExportLayer, IBrowserSkinType):
    """Base skin to export content in HTML.
    """

class IDefaultHTMLExportSkin(IHTMLExportSkin, ISilvaLayer):
    """Default skin to export content in HTML
    """
    grok.skin(u"Default HTML export")

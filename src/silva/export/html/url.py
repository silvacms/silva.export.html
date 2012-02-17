
from Acquisition import aq_parent

from zope.publisher.browser import TestRequest
from silva.export.html.skin import IHTMLExportLayer
from silva.core.references.utils import relative_path
from silva.core.interfaces import IPublishable, IContainer, IAsset


class HTMLContentUrl(object):

    def __init__(self, root, extension='html'):
        if not IContainer.providedBy(root):
            root = aq_parent(root)
        self._origin = root.getPhysicalPath()
        self.extension = extension

    def __call__(self, content):
        if IContainer.providedBy(content):
            path = list(content.getPhysicalPath()) + [
                'index.' + self.extension]
        elif IPublishable.providedBy(content):
            path = list(aq_parent(content).getPhysicalPath()) + [
                content.getId() + '.' + self.extension]
        elif IAsset.providedBy(content):
            path = list(aq_parent(content).getPhysicalPath()) + [
                content.get_filename()]
        else:
            path = content.getPhysicalPath()
        return '/'.join(relative_path(self._origin, path))


class HTMLExportRequest(TestRequest):

    def __init__(self, content):
        super(HTMLExportRequest, self).__init__(skin=IHTMLExportLayer)
        self.other = {}
        self.getHTMLUrl = HTMLContentUrl(content)


class AbsoluteURL(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def url(self, preview=False):
        return self.request.getHTMLUrl(self.context)

    def preview(self):
        return self.url(preview=True)

    __str__ = __call__ = __repr__ = __unicode__ = url

    def breadcrumbs(self):
        return []

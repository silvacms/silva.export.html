
from cStringIO import StringIO
from zipfile import ZipFile, ZIP_DEFLATED
import logging

from five import grok
from zope import schema
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary
from zope.component import getMultiAdapter, getUtility, getUtilitiesFor
from zope.interface import Interface
from zope.publisher.interfaces.browser import IBrowserSkinType

from silva.core.interfaces import IPublishable, IContainer, IContentExporter
from silva.core.interfaces import IAsset, IAssetData
from silva.core.services.utils import walk_silva_tree
from silva.core.references.interfaces import IReferenceService
from silva.export.html.url import HTMLExportRequest, HTMLContentUrl
from silva.export.html.skin import IHTMLExportSkin
from silva.core.interfaces.errors import ExternalReferenceError
from silva.translations import translate as _

logger = logging.getLogger('silva.export.html')


class Exporter(object):

    def __init__(self, root, archive, export_skin):
        self.root = root
        self.archive = archive
        self.export_skin = export_skin
        self.references = []
        self.get_references = getUtility(IReferenceService).get_references_from
        self.get_archive_name = HTMLContentUrl(root)

    def export_content(self):
        for content in walk_silva_tree(self.root, requires=IPublishable):
            if IContainer.providedBy(content):
                continue
            viewable = content.get_viewable()
            if viewable is not None:
                self.archive.writestr(
                    self.get_archive_name(content),
                    getMultiAdapter(
                        (content, HTMLExportRequest(content, self.export_skin)),
                        name='index.html')().encode('utf-8'))
                self.references.extend(self.get_references(viewable))

    def export_assets(self):
        seen = set()
        for reference in self.references:
            target = reference.target
            if target is None or not IAsset.providedBy(target):
                continue
            if not reference.is_target_inside_container(self.root):
                raise ExternalReferenceError(
                    _(u"External references"),
                    self.root, reference.target, self.root)
            path = self.get_archive_name(target)
            if path in seen:
                continue
            seen.add(path)
            self.archive.writestr(path, IAssetData(target).getData())

    def export(self):
        self.export_content()
        self.export_assets()


@grok.provider(IContextSourceBinder)
def html_skin(context):
    terms = []
    for name, skin in getUtilitiesFor(IBrowserSkinType):
        if skin.extends(IHTMLExportSkin):
            terms.append(SimpleTerm(
                    value=skin, token=skin.__identifier__, title=name))
    return SimpleVocabulary(terms)


class IExportOptions(Interface):
    html_skin = schema.Choice(
        title=_("HTML export skin"),
        source=html_skin,
        required=True)


class HTMLExporter(grok.Adapter):
    """Export content to HTML.
    """
    grok.provides(IContentExporter)
    grok.context(IPublishable)
    grok.name('html')

    name = "HTML (zip)"
    extension = "zip"
    options = IExportOptions

    def export(self, html_skin, **options):
        output = StringIO()
        archive = ZipFile(output, "w", ZIP_DEFLATED)
        Exporter(self.context, archive, html_skin).export()
        archive.close()
        return output.getvalue()

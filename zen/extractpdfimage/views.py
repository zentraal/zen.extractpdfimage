import transaction
import logging
from zope.component import getUtility
from Products.statusmessages.interfaces import IStatusMessage
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from plone.namedfile.file import NamedBlobImage
from plone.namedfile.file import NamedImage
from plone.registry.interfaces import IRegistry
from eea.converter.convert import Convert

logger = logging.getLogger('zen.extractpdfimage')


class ExtractCoverImage(BrowserView):
    def __call__(self):
        result = self.create_coverimage()
        dst_url = self.context.absolute_url() + '/view'
        if result:
            messages = IStatusMessage(self.request)
            messages.add(
                u"The cover image has been saved into the image field",
                type=u"success")
            return self.request.response.redirect(dst_url)

    def create_coverimage(self, obj=None):
        if not obj:
            obj = self.context
        registry = getUtility(IRegistry)
        dst_field_name = registry['zen.extractpdfimage.destfield']
        ffield = obj.file
        ifield = hasattr(obj, dst_field_name)
        # if the `dst_field_name` field is not present we are not in
        # the proper context
        if not ifield or ffield.contentType != 'application/pdf':
            return
        conv = Convert()
        imagedata = conv(ffield.data, **{
            'data_from': '.pdf',
            'data_to': '.png',
        })
        try:
            image = NamedBlobImage(imagedata, 'image/png', u'image.png')
        except:
            image = NamedImage(imagedata, 'image/png', u'image.png')
        setattr(obj, dst_field_name, image)
        return True


class BulkCoverImage(ExtractCoverImage):

    def __call__(self):
        catalog = getToolByName(self.context, name="portal_catalog")
        brains = catalog(
            object_provides="plone.app.contenttypes.interfaces.IFile")
        for b in brains:
            obj = b.getObject()
            self.create_coverimage(obj)
            transaction.commit()
            logger.info('Analized %s - %s' % (obj.Title(), obj.absolute_url()))

        return 'OK!'

from OFS.Image import File
from zope.component import getUtility
from Products.statusmessages.interfaces import IStatusMessage
from Products.Five.browser import BrowserView
from plone.registry.interfaces import IRegistry
from eea.converter.convert import Convert


class ExtractCoverImage(BrowserView):
    def __call__(self):
        obj = self.context
        registry = getUtility(IRegistry)
        dst_field_name = registry['zen.extractpdfimage.destfield']
        ffield = obj.getField('file')
        ifield = obj.getField(dst_field_name)
        # if the `dst_field_name` field is not present we are not in
        # the proper context
        if not ifield or ffield.getContentType(obj) != 'application/pdf':
            return
        conv = Convert()
        imagedata = conv(ffield.get(obj).data, **{
            'data_from': '.pdf',
            'data_to': '.png',
        })
        image = File('ignored-id', 'ignored-title', imagedata, 'image/png')
        obj.getField(dst_field_name).set(obj, image)
        dst_url = obj.absolute_url() + '/view'
        messages = IStatusMessage(self.request)
        messages.add(
            u"The cover image has been saved into the image field",
            type=u"success")
        return self.request.response.redirect(dst_url)

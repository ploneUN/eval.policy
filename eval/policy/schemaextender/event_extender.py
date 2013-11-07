from archetypes.schemaextender.field import ExtensionField
from archetypes.schemaextender.interfaces import IOrderableSchemaExtender
from archetypes.schemaextender.interfaces import IBrowserLayerAwareExtender
from Products.Archetypes import atapi
from Products.ATContentTypes.interfaces import IATContentType
from zope.interface import Interface
from five import grok
from eval.policy.interfaces import IProductSpecific
from eval.policy import MessageFactory as _
from Products.ATContentTypes.interfaces.event import IATEvent

# Visit http://pypi.python.org/pypi/archetypes.schemaextender for full 
# documentation on writing extenders

class ExtensionFileField(ExtensionField, atapi.FileField):
    pass

class EventExtender(grok.Adapter):

    # This applies to all AT Content Types, change this to
    # the specific content type interface you want to extend
    grok.context(IATEvent)
    grok.name('eval.policy.event_extender')
    grok.implements(IOrderableSchemaExtender, IBrowserLayerAwareExtender)
    grok.provides(IOrderableSchemaExtender)

    layer = IProductSpecific

    fields = [
        # add your extension fields here
        ExtensionFileField(
            name='attachment1',
            widget=ExtensionFileField._properties['widget'](
                label='File Attachment 1',
                description=_("If you have a list of participants, an agenda "
                    "or other supportive documentation click browse and "
                    "select the file to be uploaded.")
            )
        ),
        ExtensionFileField(
            name='attachment2',
            widget=ExtensionFileField._properties['widget'](
                label='File Attachment 2',
                description=_("If you have a list of participants, an agenda "
                    "or other supportive documentation click browse and "
                    "select the file to be uploaded.")
            )
        ),
        ExtensionFileField(
            name='attachment3',
            widget=ExtensionFileField._properties['widget'](
                label='File Attachment 3',
                description=_("If you have a list of participants, an agenda "
                    "or other supportive documentation click browse and "
                    "select the file to be uploaded.")
            )
        ),
        ExtensionFileField(
            name='attachment4',
            widget=ExtensionFileField._properties['widget'](
                label='File Attachment 4',
                description=_("If you have a list of participants, an agenda "
                    "or other supportive documentation click browse and "
                    "select the file to be uploaded.")
            )
        ),
        ExtensionFileField(
            name='attachment5',
            widget=ExtensionFileField._properties['widget'](
                label='File Attachment 5',
                description=_("If you have a list of participants, an agenda "
                    "or other supportive documentation click browse and "
                    "select the file to be uploaded.")
            )
        ),
    ]

    def __init__(self, context):
        self.context = context

    def getFields(self):
        return self.fields

    def getOrder(self, schematas):
        # you may reorder the fields in the schemata here
        return schematas

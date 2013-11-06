from zope import schema
from zope.component import getMultiAdapter
from zope.formlib import form

from plone.app.portlets.browser import z3cformhelper
from z3c.form import field

from plone.formwidget.contenttree import ObjPathSourceBinder
from z3c.relationfield.schema import RelationList, RelationChoice

from zope.interface import implements

from plone.app.portlets.portlets import base
from plone.memoize.instance import memoize
from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.cache import render_cachekey

from Acquisition import aq_inner
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from eval.policy import MessageFactory as _

class IMissionReportStatistics(IPortletDataProvider):
    """
    Define your portlet schema here
    """
    pass

class Assignment(base.Assignment):
    implements(IMissionReportStatistics)

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    @property
    def title(self):
        return _('Mission Report Statistics')

class Renderer(base.Renderer):
    
    render = ViewPageTemplateFile('templates/missionreportstatistics.pt')

    @property
    def available(self):
        return True

class AddForm(z3cformhelper.AddForm):
    fields = field.Fields(IMissionReportStatistics)
    label = _(u"Add Mission Report Statistics")
    description = _(u"")

    def create(self, data):
        return Assignment(**data)

class EditForm(z3cformhelper.EditForm):
    fields = field.Fields(IMissionReportStatistics)
    label = _(u"Edit Mission Report Statistics")
    description = _(u"")

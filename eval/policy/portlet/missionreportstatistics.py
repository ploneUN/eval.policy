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
from plone.app.vocabularies.catalog import SearchableTextSourceBinder
from plone.app.form.widgets.uberselectionwidget import UberSelectionWidget

from Acquisition import aq_inner
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from eval.policy import MessageFactory as _

from operator import itemgetter
from heapq import nlargest

from time import time
from zope.annotation.interfaces import IAnnotations
from persistent.dict import PersistentDict
from AccessControl import getSecurityManager
import Missing

from ploneun.vocabulary import resolve_value

class IMissionReportStatistics(IPortletDataProvider):
    """
    Define your portlet schema here
    """

    target_facility = schema.Choice(
        title=_(u"Target mission facility"),
        description=_(u"Find the facility which provides the items to list"),
        required=True,
        source=SearchableTextSourceBinder(
            {'portal_type': ('ploneun.missions.missionfacility')},
            default_query='path:'))

    always_update = schema.Bool(
        title=_(u'Always update'),
        description=_(u'If this is checked, the portlet will always be updated '
                    'on every page refresh. Else, it\'ll only update when '
                    'force_statsportlet_update=True exist in GET parameter'),
        required=True,
        default=True
    )


class Assignment(base.Assignment):
    implements(IMissionReportStatistics)

    target_facility = None
    always_update = True

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    @property
    def title(self):
        return _('Mission Report Statistics')

class Renderer(base.Renderer):
    
    render = ViewPageTemplateFile('templates/missionreportstatistics.pt')

    anno_key = 'eval.policy.missionstatscache'

    def update_cache(self):
        anno = IAnnotations(self.data)
        anno.setdefault(self.anno_key, PersistentDict())
        cache = anno[self.anno_key]
        cache['total'] = self._total()
        cache['international_count'] = self._international_count()
        cache['domestic_count'] = self._domestic_count()
        cache['themes'] = self._themes()
        cache['themes_international'] = self._themes_international()
        cache['themes_domestic'] = self._themes_domestic()
        cache['domestic'] = self._domestic()
        cache['international'] = self._international()
        cache['percent_missions_with_reports'] = (
            self._percent_missions_with_reports()
        )

    def cache(self):
        if (self.request.get('force_statsportlet_update', None) or 
                self.data.always_update):
            self.update_cache()
        anno = IAnnotations(self.data)
        anno.setdefault(self.anno_key, PersistentDict())
        cache = anno[self.anno_key]
        if not cache.has_key('total'):
            self.update_cache()
        return cache

    def country_title(self, country):
        if not country:
            return ''
        return resolve_value(self.context, country,
                            'ploneun.vocabulary.country')

    def theme_title(self, theme):
        if not theme:
            return ''
        return resolve_value(self.context, theme,
                            'ilo.vocabulary.themes')

    def mostcommon(self, iterable, n=None):
        """Return a sorted list of the most common to least common elements and
        their counts.  If n is specified, return only the n most common elements.
        """

        # http://code.activestate.com/recipes/347615/ (Raymond
        # Hettinger)

        bag = {}
        bag_get = bag.get
        for elem in iterable:
            bag[elem] = bag_get(elem, 0) + 1
        if n is None:
            return sorted(bag.iteritems(), key=itemgetter(1), reverse=True)
        it = enumerate(bag.iteritems())
        nl = nlargest(n, ((cnt, i, elem) for (i, (elem, cnt)) in it))
        return [(elem, cnt) for cnt, i, elem in nl]


    def _top_three_themes(self, reports):
        #grab all available themes

        themes = []

        for r in reports:
            values = r.ilo_themes
            if values == Missing.Value:
                continue
            themes += values

        #We currently filter out Other until it's not top item after
        #adding new themes to MissionReports

        top = self.mostcommon(themes)

        return top[:3] + ([('',0)] * (3-len(top[:3])))

    def _top_three_countries(self, reports):
        #grab all available themes

        countries = []

        for r in reports:
            value = r.ploneun_country
            if value == Missing.Value:
                continue
            countries.append(value)

        #We currently filter out Other until it's not top item after
        #adding new themes to MissionReports

        top = self.mostcommon(countries)

        return top[:3] + ([('',0)] * (3-len(top[:3])))


    @memoize
    def facility(self):
        facility_path = self.data.target_facility
        if not facility_path:
            return None

        if facility_path.startswith('/'):
            facility_path = facility_path[1:]

        if not facility_path:
            return None

        portal_state = getMultiAdapter((self.context, self.request),
                                       name=u'plone_portal_state')
        portal = portal_state.portal()
        if isinstance(facility_path, unicode):
            # restrictedTraverse accepts only strings
            facility_path = str(facility_path)

        result = portal.unrestrictedTraverse(facility_path, default=None)
        if result is not None:
            sm = getSecurityManager()
            if not sm.checkPermission('View', result):
                result = None
        return result

    @property
    def available(self):
        return True

    def _search(self, **kwargs):
        facility = self.facility()
        query = {
            'path': {
                'query': '/'.join(facility.getPhysicalPath()),
                'depth': 10
            },
            'portal_type': 'ploneun.missions.missionreport',
# XXX enable this later
            'review_state': 'internally_published'
        }
        query.update(kwargs)
        return self.context.portal_catalog(query)

    def _total(self):
        reports = self._search()
        return len(reports)

    def _international_count(self):
        reports = self._search(ploneun_missionscope='International')
        return len(reports)

    def _domestic_count(self):
        reports = self._search(ploneun_missionscope='National')
        return len(reports)

    def _themes(self):
        reports = self._search()
        return self._top_three_themes(reports)

    def _themes_international(self):
        reports = self._search(ploneun_missionscope='International')
        return self._top_three_themes(reports)

    def _themes_domestic(self):
        reports = self._search(ploneun_missionscope='National')
        return self._top_three_themes(reports)

    def _domestic(self):
        reports = self._search(ploneun_missionscope='National')
        return self._top_three_countries(reports)

    def _international(self):
        reports = self._search(ploneun_missionscope='International')
        return self._top_three_countries(reports)

    def _percent_missions_with_reports(self):
        all_reports = self._search()
        submitted_reports = self._search(ploneun_has_missionreport=True)
        return int((len(submitted_reports) * 1.0)/len(all_reports) * 100)


class AddForm(base.AddForm):
    form_fields = form.Fields(IMissionReportStatistics)
    form_fields['target_facility'].custom_widget = UberSelectionWidget
    label = _(u"Add Mission Report Statistics")
    description = _(u"")

    def create(self, data):
        return Assignment(**data)

class EditForm(z3cformhelper.EditForm):
    form_fields = form.Fields(IMissionReportStatistics)
    form_fields['target_facility'].custom_widget = UberSelectionWidget
    label = _(u"Edit Mission Report Statistics")
    description = _(u"")

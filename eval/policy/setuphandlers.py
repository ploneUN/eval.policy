from collective.grok import gs
from eval.policy import MessageFactory as _

@gs.importstep(
    name=u'eval.policy', 
    title=_('eval.policy import handler'),
    description=_(''))
def setupVarious(context):
    if context.readDataFile('eval.policy.marker.txt') is None:
        return
    portal = context.getSite()

    # do anything here

from django.urls import path
from .views import *
from rest_framework.routers import DefaultRouter
from django.urls.conf import include

router=DefaultRouter()

router.register('showteam', ShowteamView, basename='showteam')
router.register('createteam', CreateteamView, basename='createteam')
router.register('showagent', ShowagentView, basename='showagent')
router.register('soptypes', Showsoptypes, basename='soptypes')
router.register('lob', Showlob, basename='lob')
router.register('reporting', Showreporting, basename='reporting')
router.register('allteam', Showall, basename='allteam')
router.register('allagent', Showagent, basename='allagent')
router.register('subsop', Showsubsop, basename='subsop')

urlpatterns = [
    path('login/', loginview, name='Login'),
    path('refresh_token/', refresh_token_view , name='Refresh'),
    path('', include(router.urls))
    # path('showteam/', ShowteamView.as_view()),
    # path('showagent/', ShowagentView.as_view()),
    # path('soptypes/', Showsoptypes.as_view()),
    # path('lob/', Showlob.as_view()),
    # path('reporting/', Showreporting.as_view()),
    # path('allteam/', Showall.as_view()),
    # path('allagent/', Showagent.as_view())
]

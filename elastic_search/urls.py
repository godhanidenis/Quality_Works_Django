from django.urls import path
from .views import *

urlpatterns = [
    path('', elasticview.as_view()),
    # path('alldata/', Showalldata.as_view()),
    # path('datefilter/', Datefilterview.as_view()),
    # path('lobfilter/', Lobfilterview.as_view()),
    # path('teamfilter/', Teamfilterview.as_view()),
    # path('agentfilter/', Agentfilterview.as_view()),
    path('allfilter/', Allfilterview.as_view())
]

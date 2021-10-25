from django.urls import path
from .views import *

urlpatterns = [
    path('', elasticview.as_view()),
    path('allfilter/', Allfilterview.as_view()),
    path('softskill/', Softskillview.as_view()),
    path('process_knowledge/', Processknowledgeview.as_view()),
    path("sentiment/", Sentimentview.as_view()),
    path("salutation/", Salutationview.as_view()),
    path("callclosure/", Callclosureview.as_view()),
    path("voice/",Voiceview.as_view())
]

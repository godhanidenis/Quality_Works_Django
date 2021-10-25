from rest_framework.decorators import api_view,permission_classes
from rest_framework.response import Response
from django.contrib.auth import get_user_model
import jwt
from rest_framework.views import APIView
from .utils import token
from rest_framework import exceptions
import utils.response_handler as rh
from rest_framework.permissions import AllowAny
from django.views.decorators.csrf import ensure_csrf_cookie,csrf_protect
from decouple import config
from .models import *
from .serializers import *
from rest_framework.viewsets import ViewSet

User = get_user_model()

@api_view(['POST'])
@permission_classes([AllowAny])
@ensure_csrf_cookie
def loginview(request):
    username=request.data.get('username')
    password=request.data.get('password')
    user=User.objects.filter(username=username).first()
    if user and user.check_password(password):
        access_token = token.generate_access_token(user)
        refresh_token = token.generate_refresh_token(user)
        response = Response()
        response.set_cookie(key="refresh_token", value=refresh_token, httponly=True, max_age=7*24*60*60)
        response.data = {
        "error":False,
        "data":{
            'access_token': access_token,
        },
        'message':'jwt token genereted'
        }
        return response 
    else:
        raise Exception("username and password does not exist")
   

@api_view(['POST'])
@csrf_protect
@permission_classes([AllowAny])
def refresh_token_view(request):
    User = get_user_model()
    refresh_token = request.COOKIES.get('refresh_token')
    if refresh_token is None:
        raise exceptions.AuthenticationFailed(
            'Authentication credentials were not provided.')
    try:
        payload = jwt.decode(
            refresh_token, config("REFRESH_TOKEN_SECRET"), algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        raise exceptions.AuthenticationFailed(
            'expired refresh token, please login again.')

    user = User.objects.filter(username=payload.get('username')).first()
    if user is None:
        raise exceptions.AuthenticationFailed('User not found')

    if not user.is_active:
        raise exceptions.AuthenticationFailed('user is inactive')

    access_token = token.generate_access_token(user)
    r=rh.ResponseMsg(data={'access_token': access_token},error=False,msg="access token updated")
    return Response(r.response)

class ShowteamView(ViewSet):
    def create(self, request, format=None):
        id=request.data.get('id')
        # datas=Teams.objects.filter(LOB__id=id, LOB__User__id=request.user.id).all()
        datas=Teams.objects.filter(LOB__id=id).all()
        serializer=Teamserializer(datas, many=True)
        r=rh.ResponseMsg(data=serializer.data,error=False,msg="Teams data show")
        return Response(r.response)
           
class ShowagentView(ViewSet):
    def create(self, request, format=None):
        id=request.data.get('id')
        # id=json.loads(id)
        datas=Agents.objects.filter(Team__id__in=id).all()
        serializer=Agentserializer(datas, many=True)
        r=rh.ResponseMsg(data=serializer.data,error=False,msg="Agent data show")
        return Response(r.response)

class Showsoptypes(ViewSet):
    def list(self,request,format=None):
        obj=SOP_Types.objects.all()
        serializer= SOPTypesserializer(obj, many=True)
        r=rh.ResponseMsg(data=serializer.data,error=False,msg="ALL Sop types data show")
        return Response(r.response)

class Showlob(ViewSet):
    def list(self,request,format=None):
        # obj=LOB.objects.filter(User__id=request.user.id)
        obj=LOB.objects.all()
        serializer= LOBserializer(obj, many=True)
        r=rh.ResponseMsg(data=serializer.data,error=False,msg="ALL LOB data show")
        return Response(r.response)

class Showreporting(ViewSet):
    def list(self,request,format=None):
        # datas=Reporting.objects.filter(User__id=request.user.id).all()
        datas=Reporting.objects.all()
        serializer=Reportingserializer(datas, many=True)
        r=rh.ResponseMsg(data=serializer.data,error=False,msg="ALL Reporting data shows")
        return Response(r.response)

class Showall(ViewSet):
    def create(self,request,format=None):
        id=request.data.get('Team_Ids')
        datas=Teams.objects.filter(id__in=id)
        serializer=Teamserializer(datas, many=True)
        r=rh.ResponseMsg(data=serializer.data,error=False,msg="Teams data show")
        return Response(r.response)

class Showagent(ViewSet):
    def create(self,request,format=None):
        id=request.data.get('Agent_Ids')
        datas=Agents.objects.filter(id__in=id)
        serializer=Agentserializer(datas, many=True)
        r=rh.ResponseMsg(data=serializer.data,error=False,msg="Agent data show")
        return Response(r.response)    


from functools import partial
import json
from rest_framework.decorators import api_view,permission_classes
from rest_framework.response import Response
from django.contrib.auth import get_user_model
import jwt
from rest_framework.serializers import Serializer
from rest_framework.generics import GenericAPIView
from .utils import token
from rest_framework import exceptions
import utils.response_handler as rh
from rest_framework.permissions import AllowAny
from django.views.decorators.csrf import ensure_csrf_cookie,csrf_protect
from decouple import config
from .models import *
from .serializers import *
from rest_framework.viewsets import ViewSet
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

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
        response.set_cookie(key="refresh_token", value=refresh_token, httponly=True, samesite=None, secure=True, max_age=7*24*60*60)
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
    token_param_config = openapi.Parameter(
        'id', in_=openapi.IN_QUERY, description='integer', type=openapi.TYPE_INTEGER)

    @swagger_auto_schema(manual_parameters=[token_param_config])
    def create(self, request, format=None):
        id=request.data.get('id')
        print("Id:",id)
        # datas=Teams.objects.filter(LOB__id=id, LOB__User__id=request.user.id).all()
        datas=Teams.objects.filter(LOB__id=id,LOB__User__id=1).all()
        serializer=Teamserializer(datas, many=True)
        r=rh.ResponseMsg(data=serializer.data,error=False,msg="Teams data show")
        return Response(r.response)
           
class ManageteamView(ViewSet):
    def list(self,request,format=None):
        obj=Teams.objects.all()
        serializer=Teamserializer(obj, many=True)
        r=rh.ResponseMsg(data=serializer.data,error=False,msg="Teams data Get Successfully")
        return Response(r.response)

    def create(self, request, format=None):
        team_name=request.data.get("team_name")
        no_agents=request.data.get("no_agents")
        locations=request.data.get("locations")
        reporting_manager_id=request.data.get("reporting_manager_id")
        lob_id_list=request.data.get("lob_id_list")
        # lob_id_list=json.loads(lob_id_list)
        new_obj=Teams(Team_name=team_name,No_agentns=no_agents,Locations=locations,Reporting_manager_id=reporting_manager_id)
        new_obj.save()
        for i in lob_id_list:
            new_obj.LOB.add(str(i))
        r=rh.ResponseMsg(data={},error=False,msg="New Team Create Successfully!!")
        return Response(r.response)

    def update(self, request, pk=None):
        team_name=request.data.get("Team_name")
        lob_id_list=request.data.get("LOB")
        reporting_manager=request.data.get("Reporting_manager")
        location=request.data.get("Locations")
        no_agents=request.data.get("No_agentns")
        # lob_id_list=json.loads(lob_id_list)
        obj=Teams.objects.filter(id=pk).first()
        obj.Team_name=team_name
        obj.No_agentns=no_agents
        obj.Locations=location
        obj.Reporting_manager=Reporting_Manager.objects.get(id=reporting_manager)
        obj.LOB.set("")
        for i in lob_id_list:
            obj.LOB.add(str(i))
        obj.save()
        r=rh.ResponseMsg(data={}  ,error=True,msg="Team data updated succeessfully")
        return Response(r.response)

    def destroy(self, request, pk=None):
        team=Teams.objects.filter(id=pk).first()
        team.delete()
        r=rh.ResponseMsg(data={},error=False,msg="Team record delete successfully")
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

    def create(self,request,format=None):
        User=1
        #User=request.user.id
        Sop_name=request.data.get('Sop_name')
        new_object=SOP_Types(Sop_name=Sop_name,User_id=User)
        new_object.save()
        r=rh.ResponseMsg(data={},error=False,msg="New SOP created")
        return Response(r.response)
    
class Showsubsop(ViewSet):
    def list(self,request,format=None):
        obj=SOP.objects.all()
        serializer= SOPserializer(obj, many=True)
        r=rh.ResponseMsg(data=serializer.data,error=False,msg="ALL SOP sub type data show")
        return Response(r.response)

    def create(self,request, fromat=None):
        sop_type_id=request.data.get("sop_type_id")
        sop_sub_type=request.data.get("sub_sop")
        new_object=SOP.objects.create(Sop_types_id=sop_type_id,Sop_sub_type=sop_sub_type)
        new_object.save()
        obj=SOP.objects.filter(id=new_object.id).first()
        serializer= SOPserializer(obj)
        r=rh.ResponseMsg(data=serializer.data,error=False,msg="New sub sop create successfully")
        return Response(r.response)

    def update(self, request, pk=None):
        data=request.data
        sub_sop=SOP.objects.filter(id=pk).first()
        serializer = SOPserializer(sub_sop, data=data)
        if serializer.is_valid():
            serializer.save()
            r=rh.ResponseMsg(data={},error=False,msg="data of sub sop updated successfully")
            return Response(r.response)
        r=rh.ResponseMsg(data={},error=True,msg="data of sub sop not updated")
        return Response(r.response)

    def destroy(self, request, pk=None):
        sub_sop=SOP.objects.filter(id=pk).first()
        sub_sop.delete()
        r=rh.ResponseMsg(data={},error=False,msg="record delete successfully")
        return Response(r.response)

class Showlob(ViewSet):
    def list(self,request,format=None):
        # obj=LOB.objects.filter(User__id=request.user.id)
        obj=LOB.objects.filter(User__id=1)
        serializer= LOBserializer(obj, many=True)
        r=rh.ResponseMsg(data=serializer.data,error=False,msg="ALL LOB data show")
        return Response(r.response)

    def create(self,request, fromat=None):
        User_id=1
        #User_id=request.user.id
        lob_name=request.data.get('lob_name')
        new_object=LOB.objects.create(Lob_name=lob_name,User_id=User_id)
        new_object.save()
        r=rh.ResponseMsg(data={},error=False,msg="New LOB create successfully")
        return Response(r.response)

    def update(self, request, pk=None,*args, **kwargs):
        data=request.data
        lob=LOB.objects.filter(id=pk).first()
        serializer=LOBserializer(lob,data=data,partial=True)
        print(serializer)
        if serializer.is_valid():
            serializer.save()
            r=rh.ResponseMsg(data={},error=False,msg="data of lob updated successfully")
            return Response(r.response)
        r=rh.ResponseMsg(data={},error=True,msg="data of lob not updated")
        return Response(r.response)
        
    def destroy(self, request, pk=None):
        sub_sop=LOB.objects.filter(id=pk).first()
        sub_sop.delete()
        # team_del=Teams.objects.filter(LOB__exact=None)
        # team_del.delete()
        r=rh.ResponseMsg(data={},error=False,msg="record delete successfully")
        return Response(r.response)
class Showreporting(ViewSet):
    def list(self,request,format=None):
        # datas=Reporting.objects.filter(User__id=request.user.id).all()
        datas=Reporting.objects.all()
        serializer=Reportingserializer(datas, many=True)
        r=rh.ResponseMsg(data=serializer.data,error=False,msg="ALL Reporting data shows")
        return Response(r.response)

class Showreportingmanager(ViewSet):
    def list(self,request,format=None):
        datas=Reporting_Manager.objects.all()
        serializer=Reportingmanagerserialiazer(datas,many=True)
        r=rh.ResponseMsg(data=serializer.data,error=False,msg="Reporting manager data show")
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


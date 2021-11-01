from django.shortcuts import render
from elasticsearch import Elasticsearch
import pandas as pd
import numpy as np
from elasticsearch import helpers
from decouple import config
from rest_framework.serializers import Serializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
import json
import utils.response_handler as rh
import random
from auth_login.models import Reporting
from auth_login.serializers import Reportingserializer
import xmltodict
from urllib.request import urlopen
import requests
# Create your views here.

es = Elasticsearch(
    cloud_id=config("cloud_id"),
    http_auth=(config("user"), config("password"))
)

def generator(df2, index):
        try:
            for c, line in enumerate(df2):
                yield{
                    '_index':index,
                    '_doc_type':'test',
                    '_id': c,
                    '_source':line,
                }
        except Exception as e:
            print(e)

class elasticview(APIView):
    def post(self,request, format=None):
        file_obj=request.data.get('file')
        print(file_obj)
        es.indices.create(index='quality_works', ignore=400)
        print(es.ping())
        df = pd.read_json(file_obj)
        df["Keyword trends"] = df["Keyword trends"].replace(np.nan, 0)
        df2= df.to_dict('records')
        # generator(df2=df2, index="quality_works")
        try:
            helpers.bulk(es, generator(df2,index="quality_works"))
            print("working")
            return Response({"msg":"success"})
        except Exception as e:
            print(e)
            return Response({"msg":"failed"})
class xml_to_json(APIView):
    def post(self, request, format=None):
        file_obj=request.data.get('file')
        # var_url =requests.get("https://b2fbb4e9e7419c26abfc058fc121da71bd7a7e80d309da9d:98c1929fdd453184896ef516b0d411378fc1bd4636f955b8api.exotel.com/v1/Accounts/thinclab1/Calls/301e58c2727277ec420a36dd0f98159p")
        dictionary = xmltodict.parse(file_obj)
        json_object = json.dumps(dictionary) 
        return Response({'received data': dictionary})

class classelasticview(APIView):
    # parser_classes = [XMLParser]
    def post(self,request, format=None):
        # file_obj=request.data.get('file')
        # print(file_obj)
        es.indices.create(index='second', ignore=400)
        print(es.ping())
        # df = pd.read_json(file_obj)
        # df["Keyword trends"] = df["Keyword trends"].replace(np.nan, 0)
        df2= request.data.get('Call')
        print(df2)
        generator(df2=df2, index="second")
        try:
            res=helpers.bulk(es, generator(df2 , index="second"))
            print("working")
            return Response({"msg":"success"})
        except Exception as e:
            print(e)
            return Response({"msg":"failed"})    
class Allfilterview(APIView):
    def post(self,request,format=None):
        LOB_id=request.data.get('Lob_id')
        team_list=request.data.get('Team_list')
        # if team_list:
        #     team_list=json.loads(team_list)
        agent_list=request.data.get('Agent_list')
        # if agent_list:
        #     agent_list=json.loads(agent_list)
        matrix_list=request.data.get('Matrix_list')
        if matrix_list:
            # matrix_list=json.loads(matrix_list)
            matrix_name=Reporting.objects.filter(id__in=matrix_list)
            Serializer=Reportingserializer(matrix_name, many=True)
            matrix_dict=Serializer.data
        start_date= request.data.get('start_date')
        end_date=request.data.get('end_date')
        search_param = {}
        aggs_dict={
                    "Teams_and_lob": {
                    "multi_terms": {
                        "size": 10000,
                        "terms": [
                        {
                        "field": "LOB_id"
                        }, {
                        "field": "Team_id"
                        }
                        ]
                    },
                    "aggs": {
                        "Teams_and_lob_name": {
                        "multi_terms": {
                            "size": 10000,
                        "terms": [
                        {
                        "field": "LOB.keyword"
                        }, {
                        "field": "Team name.keyword"
                        }
                        ]
                        }
                        }
                    }
                    }  
                }
        if (LOB_id==None and team_list==None and start_date==None and end_date==None):
            search_param["size"]=0
            search_param["aggs"]=aggs_dict
        
        else:
            data={
                    "bool": {
                    "must": []
                    }
                }
            date_query={
                        "range": {
                        "Date of call": {
                            "gte": start_date,
                            "lte": end_date
                            }
                        }
                        }
            lob_query= {
                        "match": {
                            "LOB_id": LOB_id
                        }
                        }
            team_query={
                        "terms": {
                            "Team_id": team_list
                        }
                        }
            agent_query={
                        "terms": {
                            "Agent_id": agent_list
                        }
                        }
            if(start_date and end_date):
                query=date_query
                data["bool"]["must"].append(query)
                search_param["query"]=data
                search_param["aggs"]=aggs_dict

            if(LOB_id):
                query1=lob_query
                data["bool"]["must"].append(query1)
                search_param["query"]=data
                search_param["aggs"]=aggs_dict
            
            if(team_list):
                query2=team_query
                data["bool"]["must"].append(query2)
                search_param["query"]=data
                search_param["aggs"]=aggs_dict
            
            if(agent_list):
                query3=agent_query
                data["bool"]["must"].append(query3)
                search_param["query"]=data
                search_param["aggs"]=aggs_dict
                search_param["aggs"]["Teams_and_lob"]["multi_terms"]["terms"].append({
                        "field": "Agent_id"
                        })
                search_param["aggs"]["Teams_and_lob"]["aggs"]["Teams_and_lob_name"]["multi_terms"]["terms"].append({
                        "field": "Name of associate.keyword"
                        })

        search_param=json.dumps(search_param)          
        data=es.search(index='quality_works', body=search_param)     
        sub_list=[]
        dic={}
        sub_dic={}
        column_list=["LOB","Team","Total Calls","CQ SCORES"]
        if agent_list:
            column_list=["Agent","LOB","Team","Total Calls"]
            if matrix_list:
                for j in matrix_dict:
                    dict_data=dict(j)
                    column_list.append(dict_data["Matrix_type"])
            column_list.append("CQ SCORES")
        elif matrix_list :
            column_list=["LOB","Team","Total Calls"]
            for j in matrix_dict:
                dict_data=dict(j)
                column_list.append(dict_data["Matrix_type"])
            column_list.append("CQ SCORES")
        for i in data["aggregations"]["Teams_and_lob"]["buckets"]:
            if agent_list:
                sub_dic["Agent_id"]=i["key"][2]
                sub_dic["Agent"]=i["Teams_and_lob_name"]["buckets"][0]["key"][2]
            sub_dic["LOB_id"]=i["key"][0]
            sub_dic["LOB"]=i["Teams_and_lob_name"]["buckets"][0]["key"][0]
            sub_dic["Team_id"]=i["key"][1]
            sub_dic["Team"]=i["Teams_and_lob_name"]["buckets"][0]["key"][1]
            sub_dic["Total Calls"]=i["doc_count"]
            if matrix_list:
                for j in matrix_dict:
                    dict_data=dict(j)
                    sub_dic[dict_data["Matrix_type"]]=dict_data["Weights"]
            
            sub_dic["CQ SCORES"]=random.randint(20,200)
            sub_list.append(sub_dic)
            sub_dic={}
        dic["att_array"]=column_list
        dic["data"]=sub_list
        r=rh.ResponseMsg(data=dic, error=False, msg="Filter Works Successfully!!!!!!!!!!!!!!!")
        return Response(r.response)

class Softskillview(APIView):
    def post(self,request,format=None):
        lob_id=request.data.get("Lob_id")
        team_id=request.data.get("Team_id")
        agent_id=request.data.get("Agent_id")
        start_date= request.data.get('start_date')
        end_date=request.data.get('end_date')
        fields=["Curiousity","Paraphrasing", "Active Listening","Probing", "Clarity", "Responsiveness","Rate of speech (WPM)" ,"Voice volume"]
        fields1=["Rate of speech (WPM)" ,"Voice volume"]
        final_data={}
        search_params={}
        data={
                    "bool": {
                    "must": []
                    }
                }
        date_query={
                    "range": {
                    "Date of call": {
                        "gte": start_date,
                        "lte": end_date
                        }
                    }
                    }
        lob_query= {
                    "match": {
                        "LOB_id": lob_id
                    }
                    }
        team_query={
                    "match": {
                        "Team_id":  team_id
                    }
                    }
        agent_query={
                    "match": {
                        "Agent_id": agent_id
                    }
                    }
        search_params["size"]=0
        if(start_date and end_date):
            query=date_query
            data["bool"]["must"].append(query)
            search_params["query"]=data     

        if(lob_id):
            query1=lob_query
            data["bool"]["must"].append(query1)
            search_params["query"]=data
                
        if(team_id):
            query2=team_query
            data["bool"]["must"].append(query2)
            search_params["query"]=data     
            
        if(agent_id):
            query3=agent_query
            data["bool"]["must"].append(query3)
            search_params["query"]=data
                
        for field in fields:
            if field not in fields1:
                search_params["aggs"]={
                        "Avg_softskills": {
                        "avg": {
                            "field": field
                        }
                        }
                    }
                data=es.search(index='quality_works', body=search_params)
                final_data[field]=round(data["aggregations"]["Avg_softskills"]["value"]*100,2)
                color=round(data["aggregations"]["Avg_softskills"]["value"]*100,2)
                if color<=40:
                    final_data[field+"_color"]="#D65654"
                    final_data[field+"_range"]="Low"
                elif color>40 and color<=75:
                    final_data[field+"_color"]="#F8DA77"
                    final_data[field+"_range"]="Medium"
                else:
                    final_data[field+"_color"]="#4CC57E"
                    final_data[field+"_range"]="High"

        else:
            search_params["aggs"]={
                            "Rate_of_speech": {
                            "terms": {
                                "field": "Rate of speech (WPM)",
                                "size": 10000
                            }
                            },
                            "Voice_volume": {
                            "terms": {
                                "field": "Voice volume",
                                "size": 10000
                            }}
                        }
            data=es.search(index='quality_works', body=search_params)
            rate_of_speech_list=[]
            voice_volume_list=[]
            for k in data["aggregations"]["Rate_of_speech"]["buckets"]:    
                rate_of_speech_list.append(k["key"])
            for k in data["aggregations"]["Voice_volume"]["buckets"]:
                voice_volume_list.append(round(k["key"]*100))
            final_data["rate_of_speech"]=rate_of_speech_list
            final_data["max_rate_of_speech"]=max(rate_of_speech_list)
            final_data["min_rate_of_speech"]=min(rate_of_speech_list)
            final_data["voice_volume"]=voice_volume_list
            final_data["max_voice_volume"]=max(voice_volume_list)
            final_data["min_voice_volume"]=min(voice_volume_list)
        r=rh.ResponseMsg(data=final_data, error=False, msg="Soft skills AVG Successfully GET!!!!!!!!!!!!!!!")
        return Response(r.response)

class Processknowledgeview(APIView):
    def post(self,request,format=None):
        lob_id=request.data.get("Lob_id")
        team_id=request.data.get("Team_id")
        agent_id=request.data.get("Agent_id")
        start_date= request.data.get('start_date')
        end_date=request.data.get('end_date')
        fields=["Information accuracy","Critical miss","Non-critical miss","Troubleshooting"]
        fields1=["Call trasfer rate"]
        final_data={}
        search_params={}
        data={
                    "bool": {
                    "must": []
                    }
                }
        date_query={
                    "range": {
                    "Date of call": {
                        "gte": start_date,
                        "lte": end_date
                        }
                    }
                    }
        lob_query= {
                    "match": {
                        "LOB_id": lob_id
                    }
                    }
        team_query={
                    "match": {
                        "Team_id":  team_id
                    }
                    }
        agent_query={
                    "match": {
                        "Agent_id": agent_id
                    }
                    }
        search_params["size"]=0
        if(start_date and end_date):
            query=date_query
            data["bool"]["must"].append(query)
            search_params["query"]=data
            
        if(lob_id):
            query1=lob_query
            data["bool"]["must"].append(query1)
            search_params["query"]=data
               
        if(team_id):
            query2=team_query
            data["bool"]["must"].append(query2)
            search_params["query"]=data
                 
        if(agent_id):
            query3=agent_query
            data["bool"]["must"].append(query3)
            search_params["query"]=data

        for field in fields:
            if field not in fields1:
                search_params["aggs"]={
                        "Process_knowledge_avg": {
                        "avg": {
                            "field": field
                        }
                        }
                    }
                data=es.search(index='quality_works', body=search_params)
                final_data[field]=round(data["aggregations"]["Process_knowledge_avg"]["value"]*100)
                color=round(data["aggregations"]["Process_knowledge_avg"]["value"]*100)
                if color<=40:
                    final_data[field+"_color"]="#D65654"
                elif color>40 and color<=75:
                    final_data[field+"_color"]="#F8DA77"
                else:
                    final_data[field+"_color"]="#4CC57E"
        else:
            search_params["aggs"]={
                            "call_transfer_rate": {
                            "terms": {
                                "field": "Call trasfer rate",
                                "size": 10000
                            }
                            }
                        }
            data=es.search(index='quality_works', body=search_params)
            call_transfer_rate_list=[]
            for k in data["aggregations"]["call_transfer_rate"]["buckets"]:    
                call_transfer_rate_list.append(round(k["key"]*100))
            final_data["call_transfer_rate"]=call_transfer_rate_list
            final_data["max_call_transfer_rate"]=max(call_transfer_rate_list)
            final_data["min_call_transfer_rate"]=min(call_transfer_rate_list)
        final_data["Deactivation"]=35
        final_data["Deactivation_color"]="#D65654"
        final_data["Plan Details"]=65
        final_data["Plan Details_color"]="#F8DA77"
        final_data["PORT"]=85
        final_data["PORT_color"]="#4CC57E"
        final_data["Signal"]=10
        final_data["Signal_color"]="#D65654"
        final_data["Activate"]=55
        final_data["Activate_color"]="#F8DA77"
        r=rh.ResponseMsg(data=final_data, error=False, msg="Process knowledge AVG Successfully GET!!!!!!!!!!!!!!!")
        return Response(r.response)

class Sentimentview(APIView):
    def post(self,request,format=None):
        lob_id=request.data.get("Lob_id")
        team_id=request.data.get("Team_id")
        agent_id=request.data.get("Agent_id")
        start_date= request.data.get('start_date')
        end_date=request.data.get('end_date')
        fields=["call start  sentiment (Agent)","call end sentiment (Agent)","Overall sentiment(Agent)"]
        final_data={}
        final_data={}
        search_params={}
        data={
                    "bool": {
                    "must": []
                    }
                }
        date_query={
                    "range": {
                    "Date of call": {
                        "gte": start_date,
                        "lte": end_date
                        }
                    }
                    }
        lob_query= {
                    "match": {
                        "LOB_id": lob_id
                    }
                    }
        team_query={
                    "match": {
                        "Team_id":  team_id
                    }
                    }
        agent_query={
                    "match": {
                        "Agent_id": agent_id
                    }
                    }
        search_params["size"]=0
        if(start_date and end_date):
            query=date_query
            data["bool"]["must"].append(query)
            search_params["query"]=data
               
        if(lob_id):
            query1=lob_query
            data["bool"]["must"].append(query1)
            search_params["query"]=data
                  
        if(team_id):
            query2=team_query
            data["bool"]["must"].append(query2)
            search_params["query"]=data
                
        if(agent_id):
            query3=agent_query
            data["bool"]["must"].append(query3)
            search_params["query"]=data

        for field in fields:
            search_params["aggs"]={
                            "Avg_snetiment": {
                            "avg": {
                                "field": field
                            }
                            }
                        }
            data=es.search(index='quality_works', body=search_params)
            final_data[field]=round(data["aggregations"]["Avg_snetiment"]["value"]*100)
            color=round(data["aggregations"]["Avg_snetiment"]["value"]*100)
            if color<=40:
                final_data[field+"_color"]="#D65654"
            elif color>40 and color<=75:
                final_data[field+"_color"]="#F8DA77"
            else:
                final_data[field+"_color"]="#4CC57E"
        r=rh.ResponseMsg(data=final_data, error=False, msg="Sentiments AVG Successfully GET!!!!!!!!!!!!!!!")
        return Response(r.response)

class Salutationview(APIView):
    def post(self,request,format=None):
        lob_id=request.data.get("Lob_id")
        team_id=request.data.get("Team_id")
        agent_id=request.data.get("Agent_id")
        start_date= request.data.get('start_date')
        end_date=request.data.get('end_date')
        call_opening_field=["Thanks for calling Matrix Solutions, How can I help you today?","Good Morning, Matrix Solutions. How can I able to help you?","Hello Matrix Solutions, I can help you with that!"]
        customer_authentication_field=["Can you confirm your phone number please?","is your number 1234567890","Kindly confirm your ticket number pl?"]
        on_hold_field=["Can I put you on hold while I fetch the info","Let me put you on hold while I get the needful information","Would you mind if I put you on hold to get the information"]
        final_data={}
        search_params={}
        data={
                    "bool": {
                    "must": []
                    }
                }
        date_query={
                    "range": {
                    "Date of call": {
                        "gte": start_date,
                        "lte": end_date
                        }
                    }
                    }
        lob_query= {
                    "match": {
                        "LOB_id": lob_id
                    }
                    }
        team_query={
                    "match": {
                        "Team_id":  team_id
                    }
                    }
        agent_query={
                    "match": {
                        "Agent_id": agent_id
                    }
                    }
        search_params["size"]=0
        if(start_date and end_date):
            query=date_query
            data["bool"]["must"].append(query)
            search_params["query"]=data
    
        if(lob_id):
            query1=lob_query
            data["bool"]["must"].append(query1)
            search_params["query"]=data
                  
        if(team_id):
            query2=team_query
            data["bool"]["must"].append(query2)
            search_params["query"]=data
                 
        if(agent_id):
            query3=agent_query
            data["bool"]["must"].append(query3)
            search_params["query"]=data

        call_opening_list=[]

        for field in call_opening_field:
            search_params["aggs"]={
                        "salutation_avg": {
                        "avg": {
                            "field": field
                        }
                        }
                    }
            data=es.search(index='quality_works', body=search_params)
            call_opening_dict={}
            call_opening_dict["key"]=field
            call_opening_dict["value"]=round(data["aggregations"]["salutation_avg"]["value"]*100)
            color=round(data["aggregations"]["salutation_avg"]["value"]*100)
            if color<=40:
                call_opening_dict["color"]="#D65654"
            elif color>40 and color<=75:
                call_opening_dict["color"]="#FFBF00"
            else:
                call_opening_dict["color"]="#4CC57E"
            call_opening_list.append(call_opening_dict)
            call_opening_dict={}
        final_data["Call_Opening"]=call_opening_list

        on_hold_list=[]
        for field in on_hold_field:
            search_params["aggs"]={
                        "salutation_avg": {
                        "avg": {
                            "field": field
                        }
                        }
                    }
            data=es.search(index='quality_works', body=search_params)
            on_hold_dict={}
            on_hold_dict["key"]=field
            on_hold_dict["value"]=round(data["aggregations"]["salutation_avg"]["value"]*100)
            color=round(data["aggregations"]["salutation_avg"]["value"]*100)
            if color<=40:
                on_hold_dict["color"]="#D65654"
            elif color>40 and color<=75:
                on_hold_dict["color"]="#FFBF00"
            else:
                on_hold_dict["color"]="#4CC57E"
            on_hold_list.append(on_hold_dict)
            on_hold_dict={}
        final_data["on_hold"]=on_hold_list

        customer_authentication_list=[]
        for field in customer_authentication_field:
            search_params["aggs"]={
                        "salutation_avg": {
                        "avg": {
                            "field": field
                        }
                        }
                    }
            data=es.search(index='quality_works', body=search_params)
            customer_authentication_dict={}
            customer_authentication_dict["key"]=field
            customer_authentication_dict["value"]=round(data["aggregations"]["salutation_avg"]["value"]*100)
            color=round(data["aggregations"]["salutation_avg"]["value"]*100)
            if color<=40:
                customer_authentication_dict["color"]="#D65654"
            elif color>40 and color<=75:
                customer_authentication_dict["color"]="#FFBF00"
            else:
                customer_authentication_dict["color"]="#4CC57E"
            customer_authentication_list.append(customer_authentication_dict)
            customer_authentication_dict={}
        final_data["customer_authentication"]=customer_authentication_list
        r=rh.ResponseMsg(data=final_data, error=False, msg="Salutation get successfully")
        return Response(r.response)
        
class Callclosureview(APIView):
    def post(self,request,format=None):
        lob_id=request.data.get("Lob_id")
        team_id=request.data.get("Team_id")
        agent_id=request.data.get("Agent_id")
        start_date= request.data.get('start_date')
        end_date=request.data.get('end_date')
        call_closure_field=["Thanks for calling Matrix Solutions, How can I help you today?","Good Morning, Matrix Solutions. How can I able to help you?","Hello Matrix Solutions, I can help you with that!"]
        final_data={}
        search_params={}
        data={
                    "bool": {
                    "must": []
                    }
                }
        date_query={
                    "range": {
                    "Date of call": {
                        "gte": start_date,
                        "lte": end_date
                        }
                    }
                    }
        lob_query= {
                    "match": {
                        "LOB_id": lob_id
                    }
                    }
        team_query={
                    "match": {
                        "Team_id":  team_id
                    }
                    }
        agent_query={
                    "match": {
                        "Agent_id": agent_id
                    }
                    }
        search_params["size"]=0
        if(start_date and end_date):
            query=date_query
            data["bool"]["must"].append(query)
            search_params["query"]=data
               
        if(lob_id):
            query1=lob_query
            data["bool"]["must"].append(query1)
            search_params["query"]=data
                
        if(team_id):
            query2=team_query
            data["bool"]["must"].append(query2)
            search_params["query"]=data
                
        if(agent_id):
            query3=agent_query
            data["bool"]["must"].append(query3)
            search_params["query"]=data
            
        call_opening_list=[]
        for field in call_closure_field:
            search_params["aggs"]={
                        "callclosure_avg": {
                        "avg": {
                            "field": field
                        }
                        }
                    }
            data=es.search(index='quality_works', body=search_params)
            call_opening_dict={}
            call_opening_dict["key"]=field
            call_opening_dict["value"]=round(data["aggregations"]["callclosure_avg"]["value"]*100)
            color=round(data["aggregations"]["callclosure_avg"]["value"]*100)
            if color<=40:
                call_opening_dict["color"]="#D65654"
            elif color>40 and color<=75:
                call_opening_dict["color"]="#F8DA77"
            else:
                call_opening_dict["color"]="#4CC57E"
            call_opening_list.append(call_opening_dict)
            call_opening_dict={}
        final_data["Call_Opening"]=call_opening_list
        final_data["Additional_Information"]=30
        final_data["Additional_Information_color"]="#D65654"
        final_data["Alternative_Channels"]=60
        final_data["Alternative_Channels_color"]="#F8DA77"
        final_data["Call_Summarizations"]=90
        final_data["Call_Summarizations_color"]="#4CC57E"
        r=rh.ResponseMsg(data=final_data, error=False, msg="Call Closure get successfully")
        return Response(r.response)

class Voiceview(APIView):
    def post(self,request, format=None):
        lob_id=request.data.get("Lob_id")
        team_id=request.data.get("Team_id")
        agent_id=request.data.get("Agent_id")
        start_date= request.data.get('start_date')
        end_date=request.data.get('end_date')
        voice_field=["overtalk incidents","Silence incidents"]
        final_data={}
        search_params={}
        data={
                    "bool": {
                    "must": []
                    }
                }
        date_query={
                    "range": {
                    "Date of call": {
                        "gte": start_date,
                        "lte": end_date
                        }
                    }
                    }
        lob_query= {
                    "match": {
                        "LOB_id": lob_id
                    }
                    }
        team_query={
                    "match": {
                        "Team_id":  team_id
                    }
                    }
        agent_query={
                    "match": {
                        "Agent_id": agent_id
                    }
                    }
        search_params["size"]=0
        if(start_date and end_date):
            query=date_query
            data["bool"]["must"].append(query)
            search_params["query"]=data
               

        if(lob_id):
            query1=lob_query
            data["bool"]["must"].append(query1)
            search_params["query"]=data
               
            
        if(team_id):
            query2=team_query
            data["bool"]["must"].append(query2)
            search_params["query"]=data
                
            
        if(agent_id):
            query3=agent_query
            data["bool"]["must"].append(query3)
            search_params["query"]=data
            
        search_params["size"]=0
        search_params["query"]=query
        for field in voice_field:
            search_params["aggs"]={
                    "voice_avg": {
                    "avg": {
                        "field": field
                    }
                    }
                }
            data=es.search(index='quality_works', body=search_params)
            final_data[field]=round(data["aggregations"]["voice_avg"]["value"])
        r=rh.ResponseMsg(data=final_data, error=False, msg="Call Closure get successfully")
        return Response(r.response)
        
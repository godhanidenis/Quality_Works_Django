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
from rest_framework.response import Response
# Create your views here.

es = Elasticsearch(
    cloud_id=config("cloud_id"),
    http_auth=(config("user"), config("password"))
)

def generator(df2):
        try:
            for c, line in enumerate(df2):
                yield{
                    '_index':'quality_works',
                    '_doc_type':'test',
                    '_id': c,
                    '_source':line,
                }
        except Exception as e:
            print(e)

class elasticview(APIView):
    permission_classes=[AllowAny,]

    def post(self,request, format=None):
        file_obj=request.data.get('file')
        print(file_obj)
        es.indices.create(index='quality_works', ignore=400)
        print(es.ping())
        df = pd.read_json(file_obj)
        df["Keyword trends"] = df["Keyword trends"].replace(np.nan, 0)
        df2= df.to_dict('records')
        generator(df2=df2)
        try:
            res=helpers.bulk(es, generator(df2))
            print("working")
            return Response({"msg":"success"})
        except Exception as e:
            print(e)
            return Response({"msg":"failed"})

class Allfilterview(APIView):
    permission_classes=[AllowAny,]

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
            column_list=["LOB","Team","Total Calls","Agent","CQ SCORES"]
        elif matrix_list:
            column_list=["LOB","Team","Total Calls","CQ SCORES"]
            for j in matrix_dict:
                dict_data=dict(j)
                column_list.append(dict_data["Matrix_type"])
        for i in data["aggregations"]["Teams_and_lob"]["buckets"]:
            sub_dic["LOB_id"]=i["key"][0]
            sub_dic["Team_id"]=i["key"][1]
            sub_dic["Total Calls"]=i["doc_count"]
            sub_dic["LOB"]=i["Teams_and_lob_name"]["buckets"][0]["key"][0]
            sub_dic["Team"]=i["Teams_and_lob_name"]["buckets"][0]["key"][1]
            if agent_list:
                sub_dic["Agent_id"]=i["key"][2]
                sub_dic["Agent"]=i["Teams_and_lob_name"]["buckets"][0]["key"][2]
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
from django.shortcuts import render
from elasticsearch import Elasticsearch
import pandas as pd
import numpy as np
from elasticsearch import helpers
from decouple import config
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
import json
import utils.response_handler as rh
import random
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


class Showalldata(APIView):
    permission_classes=[AllowAny,]

    def get(self,request, format=None):
        search_param = {
                    "size": 0,
                    "aggs": {
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
                    }
        data=es.search(index='quality_works', body=search_param)
        main_list=[]
        dic={}
        for i in data["aggregations"]["Teams_and_lob"]["buckets"]:
            dic["LOB_id"]=i["key"][0]
            dic["Team_id"]=i["key"][1]
            dic["total_calls"]=i["doc_count"]
            dic["LOB"]=i["Teams_and_lob_name"]["buckets"][0]["key"][0]
            dic["Team name"]=i["Teams_and_lob_name"]["buckets"][0]["key"][1]
            dic["CQ_score"]=random.randint(20,200)
            main_list.append(dic)
            dic={}
        r=rh.ResponseMsg(data=main_list, error=False, msg="All data shows successfully")
        return Response(r.response)


class Datefilterview(APIView):
    permission_classes=[AllowAny,]

    def post(self,request, format=None):
        start_date= request.data.get('start_date')
        end_date=request.data.get('end_date')
        search_param = {
                    "size": 0,
                    "query": {
                        "bool": {
                        "must": [
                            {
                            "range": {
                            "Date of call": {
                                "gte": start_date,
                                "lte": end_date
                                }
                            }
                            }
                        ]
                        }
                    }, 
                    "aggs": {
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
                    }
        data=es.search(index='quality_works', body=search_param)
        main_list=[]
        dic={}
        for i in data["aggregations"]["Teams_and_lob"]["buckets"]:
            dic["LOB_id"]=i["key"][0]
            dic["Team_id"]=i["key"][1]
            dic["total_calls"]=i["doc_count"]
            dic["LOB"]=i["Teams_and_lob_name"]["buckets"][0]["key"][0]
            dic["Team name"]=i["Teams_and_lob_name"]["buckets"][0]["key"][1]
            dic["CQ_score"]=random.randint(20,200)
            main_list.append(dic)
            dic={}
        r=rh.ResponseMsg(data=main_list, error=False, msg="date filter shows successfully")
        return Response(r.response)

class Lobfilterview(APIView):
    permission_classes=[AllowAny,]
    
    def post(self,request, format=None):
        LOB_id=request.data.get('Lob_id')
        start_date= request.data.get('start_date')
        end_date=request.data.get('end_date')
        search_param ={
                "size": 0,
                "query": {
                    "bool": {
                    "must": [
                        {
                        "range": {
                        "Date of call": {
                            "gte": start_date,
                            "lte": end_date
                            }
                        }
                        },
                        {
                        "match": {
                            "LOB_id": LOB_id
                        }
                        }
                    ]
                    }
                }, 
                "aggs": {
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
                }
        data=es.search(index='quality_works', body=search_param)
        main_list=[]
        dic={}
        for i in data["aggregations"]["Teams_and_lob"]["buckets"]:
            dic["LOB_id"]=i["key"][0]
            dic["Team_id"]=i["key"][1]
            dic["total_calls"]=i["doc_count"]
            dic["LOB"]=i["Teams_and_lob_name"]["buckets"][0]["key"][0]
            dic["Team name"]=i["Teams_and_lob_name"]["buckets"][0]["key"][1]
            dic["CQ_score"]=random.randint(20,200)
            main_list.append(dic)
            dic={}
        r=rh.ResponseMsg(data=main_list, error=False, msg="Lob filter shows successfully")
        return Response(r.response)
        
class Teamfilterview(APIView):
    permission_classes=[AllowAny,]
    
    def post(self,request, format=None):
        LOB_id=request.data.get('Lob_id')
        team_list=request.data.get('Team_list')
        # team_list=json.loads(team_list)
        start_date= request.data.get('start_date')
        end_date=request.data.get('end_date')
        search_param ={
                "size": 0,
                "query": {
                    "bool": {
                    "must": [
                        {
                        "range": {
                        "Date of call": {
                            "gte": start_date,
                            "lte": end_date
                            }
                        }
                        },
                        {
                        "match": {
                            "LOB_id": LOB_id
                        }
                        },
                        {
                        "terms": {
                            "Team_id": team_list
                        }
                        }
                    ]
                    }
                }, 
                "aggs": {
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
                }
        data=es.search(index='quality_works', body=search_param)
        main_list=[]
        dic={}
        for i in data["aggregations"]["Teams_and_lob"]["buckets"]:
            dic["LOB_id"]=i["key"][0]
            dic["Team_id"]=i["key"][1]
            dic["total_calls"]=i["doc_count"]
            dic["LOB"]=i["Teams_and_lob_name"]["buckets"][0]["key"][0]
            dic["Team name"]=i["Teams_and_lob_name"]["buckets"][0]["key"][1]
            dic["CQ_score"]=random.randint(20,200)
            main_list.append(dic)
            dic={}
        r=rh.ResponseMsg(data=main_list, error=False, msg="Team filter shows successfully")
        return Response(r.response)

class Agentfilterview(APIView):

    permission_classes=[AllowAny,]

    def post(self,request, format=None):
        LOB_id=request.data.get('Lob_id')
        team_list=request.data.get('Team_list')
        # team_list=json.loads(team_list)
        agent_list=request.data.get('Agent_list')
        # agent_list=json.loads(agent_list)
        start_date= request.data.get('start_date')
        end_date=request.data.get('end_date')
        search_param ={
                    "size": 0,
                    "query": {
                        "bool": {
                        "must": [
                            {
                            "range": {
                            "Date of call": {
                                "gte": start_date,
                                "lte": end_date
                                }
                            }
                            },
                            {
                            "match": {
                                "LOB_id": LOB_id
                            }
                            },
                            {
                            "terms": {
                                "Team_id": team_list
                            }
                            },{
                            "terms": {
                                "Agent_id": agent_list
                            }
                            }
                        ]
                        }
                    }, 
                    "aggs": {
                        "Teams_and_lob": {
                        "multi_terms": {
                            "size": 10000,
                            "terms": [
                            {
                            "field": "LOB_id"
                            }, {
                            "field": "Team_id"
                            },{
                            "field": "Agent_id"
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
                            },{
                            "field": "Name of associate.keyword"
                            }
                            ]
                            }
                            }
                        }
                        }
                        
                    }
                    }
        data=es.search(index='quality_works', body=search_param)
        main_list=[]
        dic={}
        for i in data["aggregations"]["Teams_and_lob"]["buckets"]:
            dic["LOB_id"]=i["key"][0]
            dic["Team_id"]=i["key"][1]
            dic["Agent_id"]=i["key"][2]
            dic["total_calls"]=i["doc_count"]
            dic["LOB"]=i["Teams_and_lob_name"]["buckets"][0]["key"][0]
            dic["Team name"]=i["Teams_and_lob_name"]["buckets"][0]["key"][1]
            dic["Agent name"]=i["Teams_and_lob_name"]["buckets"][0]["key"][2]
            dic["CQ_score"]=random.randint(20,200)
            main_list.append(dic)
            dic={}
        r=rh.ResponseMsg(data=main_list, error=False, msg="Agent filter shows successfully")
        return Response(r.response)
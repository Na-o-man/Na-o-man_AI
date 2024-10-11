from elasticsearch import Elasticsearch
es = Elasticsearch(["your_elastic_search_ip"])

def handler(event, context):
    memberId = event["memberId"]
    shareGroupId = event["shareGroupId"]
    sampleFaceVectorSearch = {
                                "size" : 10,
                                "_source": ["faceVector"], 
                                "query": {
                                    "term":{
                                    "memberId": memberId
                                    }
                                }
                            }
    
    sampleFaceVectorSearchResponse = es.search(index = "sample_face_vectors", body = sampleFaceVectorSearch)
    sampleVectorCount = sampleFaceVectorSearchResponse["hits"]["total"]["value"]
    tagFace = set()
    for i in range(sampleVectorCount):
        sampleVector = sampleFaceVectorSearchResponse["hits"]["hits"][i]["_source"]["faceVector"]
        nameList = faceSearch(sampleVector,shareGroupId)
        for name in nameList:
            tagFace.add(name)
    
    faceTagQuery = {
        "script": {
            "source": "ctx._source.faceTag.add(params.memberId)",
            "lang": "painless",
            "params": {
            "memberId": memberId
            }
        },
        "query": {
            "terms": {
                "name": list(tagFace)
            }
        }
    }
    es.update_by_query(index = "photos_es", body = faceTagQuery, routing= str(shareGroupId))

    
    
def faceSearch(faceVector, shareGroupId):
    shareGroupFaceSearch ={
        "_source": ["name"],
        "size" :5000,
        "min_score": 0.68,
        "query": {
            "script_score": {
                "query" : {
                    "bool" : {
                    "filter" : {
                        "term" : {
                        "shareGroupId" : shareGroupId
                        }
                    }
                    }
                },
                "script": {
                    "source": "(dotProduct(params.query_vector, 'faceVector') + 1.0)/2",
                    "params": {
                    "query_vector": faceVector
                    }
                }
            }
        }
    }
    vectorSearchResponse = es.search(index="face_vectors", body=shareGroupFaceSearch,routing = str(shareGroupId))
    tageName = list()
    hits = vectorSearchResponse["hits"]["hits"]
    for i in range(len(hits)):
        tageName.append(hits[i]["_source"]["name"])
    return tageName
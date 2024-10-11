from elasticsearch import Elasticsearch
from pytz import timezone
from datetime import datetime
import numpy as np

def elasticSearchApi(shareGroupId, imageName, faceVector, memberIdList):
    es = Elasticsearch(["your_elastic_search_ip"])
    faceVector = np.round(faceVector,9)
    doc = {
            "createdAt" : setSaveTime(),
            "name" : imageName,
            "shareGroupId" : int(shareGroupId),
            "faceVector" : faceVector.tolist(),
    }

    vectorSearch = {
        "_source": ["memberId"],
        "size" :4,
        "query": {
            "script_score": {
            "query" : {
                "bool" : {
                "filter" : {
                    "terms" : {
                    "memberId" : memberIdList
                    }
                }
                }
            },
            "script": {
                "source": "(dotProduct(params.query_vector, 'faceVector') + 1.0)/2",
                "params": {
                "query_vector": faceVector.tolist()
                }
            }
            }
        }
    }
    search = {
        "_source": ["faceTag"],
        "query": {
            "match": {
                "name": imageName
            }
        }
    }
    update = {
        "faceTag" : []
    }
    
    vectorSearchResponse = es.search(index="sample_face_vectors", body=vectorSearch)
    if vectorSearchResponse['hits']['hits'] != []:
        print("샘플 사진에서 히트")
        print(f"히트 스코어 :" + str(vectorSearchResponse['hits']['hits'][0]["_score"]))
        hit_doc = vectorSearchResponse['hits']['hits'][0]
        hit_memberId = hit_doc['_source']["memberId"]
        if(hit_doc["_score"] > 0.68):
            searchResponse = es.search(index="photos_es", body=search, routing =str(shareGroupId))
            photoEsId = searchResponse['hits']['hits'][0]['_id']
            faceTag = searchResponse['hits']['hits'][0]['_source']["faceTag"]
            if hit_memberId not in faceTag:
                faceTag.append(hit_memberId) 
                es.update(index="photos_es", id = photoEsId, body = {"doc" : {"faceTag" : faceTag}} ,routing =str(shareGroupId))
                print(f"{photoEsId} 도큐먼트에 {hit_memberId} 추가 완료")
        else:
            es.index(index="face_vectors", body=doc, routing =str(shareGroupId))
            print("전송완료")

    else:
        es.index(index="face_vectors", body=doc, routing =str(shareGroupId))
        print("전송완료")
        

def setSaveTime():
    today = datetime.now(timezone('Asia/Seoul'))
    return today.strftime("%Y-%m-%d %H:%M:%S")
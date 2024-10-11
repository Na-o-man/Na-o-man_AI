from elasticsearch import Elasticsearch
from pytz import timezone
from datetime import datetime
import numpy as np

def elasticSearchApi(faceVector, memberId):
    es = Elasticsearch(["your_elastic_search_ip"])
    faceVector = np.round(faceVector,9)
    doc = {
            "memberId" : int(memberId),
            "faceVector" : faceVector.tolist()
    }

    es.index(index="sample_face_vectors", body=doc)
    print("전송완료")
    
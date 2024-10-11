from deepface import DeepFace
import numpy as np
from PIL import Image
import boto3
import io
import cv2 
import pillow_heif
import esQuery

def handler(event, context):
    #API 데이터 로드
    photoNameList = event["photoNameList"]
    memberId = event["memberId"]
    print("photoNameList : " + str(photoNameList))
    print("memberId : " +str(memberId))

    for name in photoNameList:
        #이미지 로드
        BUCKET_NAME = "s3_bucket_name"
        s3 = boto3.client("s3")
        image_response = s3.get_object(Bucket = BUCKET_NAME, Key = "raw/" + name)
        print("이미지 로드 완료")
        image_data = image_response["Body"].read()

        try:
            image = Image.open(io.BytesIO(image_data))
        except IOError:
            heif_image = pillow_heif.read_heif(io.BytesIO(image_data))
            image = Image.frombytes(
                heif_image.mode, 
                heif_image.size, 
                bytes(heif_image.data), 
                "raw", 
                heif_image.mode, 
                heif_image.stride,
            )
        image = resize_image(image, 1000)

        # PIL 이미지를 numpy 배열로 변환
        image_np = np.array(image)
        # RGB 형식을 BGR 형식으로 변환
        image_bgr = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)
        print("이미지 numpy로 변환 완료")
        faceEmbedding = DeepFace.represent(img_path = image_bgr, model_name = "ArcFace", enforce_detection=False, detector_backend="yolov8")
        print("이미지 모델 통과")
        if len(faceEmbedding)==0:
            continue
        normalized_vector = norm(faceEmbedding)

        esQuery.elasticSearchApi(normalized_vector[0], memberId)




#이미지의 크기를 큰 쪽이 1000px이 되도록 함.
def resize_image(image, max_length):
    width, height = image.size
    if max(width, height) > max_length:
        if width > height:
            new_width = max_length
            new_height = int((max_length / width) * height)
        else:
            new_height = max_length
            new_width = int((max_length / height) * width)
        image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    return image


#list -> np.array, and ndarray is normalized
def norm(faceEmbeddings):
    normalized_vector = np.zeros((len(faceEmbeddings), 512))
    for index, i in enumerate(faceEmbeddings):
        unNorm = faceEmbeddings[index]["embedding"]
        numpy_array = np.array(unNorm)
        vector_size = np.sum(np.multiply(numpy_array,numpy_array))
        normalized_vector[index] = numpy_array / np.sqrt(vector_size)
    return normalized_vector

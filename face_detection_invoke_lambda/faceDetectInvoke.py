import boto3
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

lambda_client = boto3.client('lambda',
                             region_name='ap-northeast-2',
                             aws_access_key_id='your_s3_key',
                             aws_secret_access_key='your_s3_key'
                             )  

def handler(event, context):
    #API 데이터 로드
    nameList = event["photoNameList"]
    shareGroupId = event["shareGroupId"]
    memberIdList = event["memberIdList"]
    

    with ThreadPoolExecutor() as executor:
        future_to_name = {executor.submit(invoke_lambda, name, shareGroupId,memberIdList): name for name in nameList}

        for future in as_completed(future_to_name):
            name = future_to_name[future]
            try:
                response = future.result()
                print(f'Lambda function for {name} completed with response: {response}')
            except Exception as exc:
                print(f'Lambda function for {name} generated an exception: {exc}')
    
def invoke_lambda(name, shareGroupId, memberIdList):
    response = lambda_client.invoke(
        FunctionName="your_lamda_funtion",
        InvocationType='Event',
        Payload=json.dumps({
            "name": name,
            "shareGroupId": shareGroupId,
            "memberIdList" : memberIdList
        })
    )
    return response
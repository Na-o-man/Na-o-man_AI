FROM amazon/aws-lambda-python:3.8

RUN yum update -y
RUN yum install mesa-libGL -y
RUN yum install libglvnd-glx -y
RUN yum install gcc openssl-devel wget tar -y

RUN pip install --upgrade pip

COPY requirements.txt ${LAMBDA_TASK_ROOT}
RUN pip install --no-cache-dir -r requirements.txt

ENV DEEPFACE_HOME ${LAMBDA_TASK_ROOT}

COPY ./.deepface ${LAMBDA_TASK_ROOT}/.deepface

COPY faceDetect.py ${LAMBDA_TASK_ROOT}
COPY esQuery.py ${LAMBDA_TASK_ROOT}

CMD ["faceDetect.handler"]
FROM amazon/aws-lambda-python:3.8

COPY requirements.txt ${LAMBDA_TASK_ROOT}
RUN pip install --no-cache-dir -r requirements.txt

COPY joinShareGroup.py ${LAMBDA_TASK_ROOT}

CMD ["joinShareGroup.handler"]
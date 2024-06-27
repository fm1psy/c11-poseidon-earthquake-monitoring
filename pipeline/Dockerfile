FROM public.ecr.aws/lambda/python:latest

WORKDIR ${LAMBDA_TASK_ROOT}

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY extract.py .
COPY transform.py .
COPY load.py .
COPY sns.py .
COPY main.py .
COPY handler.py .

CMD [ "handler.handler" ]
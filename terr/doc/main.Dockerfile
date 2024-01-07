FROM python:3.10.13-bullseye
ENV HOST=clickhouse-service

RUN apt-get install git -y
RUN git clone https://github.com/Egorlop/CloudFAST
WORKDIR /CloudFAST
RUN pip install -r requirements.txt

CMD ["bash", "-c", "uvicorn main:app --host 0.0.0.0 --port 8080"]
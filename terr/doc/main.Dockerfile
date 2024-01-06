FROM python:3.10.13-bullseye

RUN apt-get install git -y
RUN git clone https://github.com/Egorlop/CloudFAST
WORKDIR /CloudFAST
RUN pip install -r requirements.txt
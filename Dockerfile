# syntax=docker/dockerfile:1

FROM arm64v8/python

WORKDIR /python-docker

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

CMD [ "python3", "-m" , "flask", "run","-p","8555"]
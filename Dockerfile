FROM --platform=$BUILDPLATFORM  alexberkovich/alpine-anaconda3

WORKDIR /python-docker

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

CMD [ "python3", "-m" , "flask", "run","-p","8555"]
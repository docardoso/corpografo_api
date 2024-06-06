FROM python:3.11
EXPOSE 5000
WORKDIR /app




#Cache-unfriendly (not sure)
#COPY . .
#RUN pip install -r requirements.txt



# Cache-friendly (not sure)
COPY ./requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY . .



#CMD find .
CMD flask run --host 0.0.0.0 --cert adhoc

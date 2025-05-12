# app/Dockerfile
FROM  python:3.13-slim

WORKDIR /app
ADD /app .

RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8501

CMD ["streamlit", "run", "Homepage.py"]

#CMD ["streamlit", "run", "app.py"]
#docker build -t ontoTEAEMS5 .
#docker run -p 8501:8501 ontoTEAEMS5
#docker image tag ontoteams eddykams/ontoteamrepo:v2
#docker push eddykams/ontoteamrepo:v2
#docker container run --publish 8501:8501 --detach --name myonotteamsapp ontoteams


#docker tag local-image:tagname new-repo:tagname
#docker push new-repo:tagname
# app/Dockerfile

FROM --platform=linux/amd64 python:3.11

WORKDIR /app
ADD /app .

RUN pip install -r requirements.txt
EXPOSE 8501

CMD ["streamlit", "run", "welcome.py"]
#ENTRYPOINT [ "streamlit", "run", "welcome.py" ]
# CMD ["streamlit", "run", "app.py"]
#docker build -t ontoTEAEMS5 .
#docker run -p 8501:8501 ontoTEAEMS5
# docker container run --publish 8501:8501 --detach --name myonotteamsapp ontoteams
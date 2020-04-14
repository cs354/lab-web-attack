FROM python:3-alpine
WORKDIR /usr/src/app
RUN cd /usr/src/app
ADD app /usr/src/app
ADD requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 5000
#CMD FLASK_ENV=development python -m flask run --host=0.0.0.0
CMD python -m flask run --host=0.0.0.0
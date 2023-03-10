FROM python:3.9
ENV PYTHONUNBUFFERED=1 PYTHONPATH=$PYTHONPATH:/Project/src:/Project/src/aioVextractor 
WORKDIR /Project
COPY . /Project
RUN pip install -r requirements.txt && \
    pyppeteer-install

CMD cd aioVextractor && gunicorn -c gunicorn-conf.py  demo-api:app

#FROM python:3
#RUN  apt install libcurl4-openssl-dev libssl-dev
FROM python:3
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
COPY requirements.txt /code/
COPY . /code/

#ADD ./requirements.txt requirements.txt
COPY ./manage.py manage.py
#COPY ./authentication authentication
#COPY ./program program
COPY ./pda pda
#COPY ./static static
COPY ./.env  .env
COPY ./.env .env
COPY ./apps apps

# Install requirements
RUN pip install -r requirements.txt
RUN  python3 manage.py collectstatic --noinput
COPY ./static static
#CMD  python3 manage.py run server --bind 0.0.0.0:8000

FROM python
ENV PYTHONUNBUFFERED 1
RUN mkdir /web_django
WORKDIR /web_django
COPY requirements.txt /web_django/
ENV PORT=8000
EXPOSE 8000
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
ADD . /web_django/
CMD python manage.py runserver 0.0.0.0:8000
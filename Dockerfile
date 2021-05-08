from python:3.8.5-slim

ADD requirements.txt /app/requirements.txt

RUN pip3 install --no-cache-dir -r /app/requirements.txt

COPY . /app/

WORKDIR /app/

CMD ["gunicorn", "--bind", ":8000", "bananaImageRepository.wsgi:application"]
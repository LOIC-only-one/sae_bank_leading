FROM debian:slim

ENV APP=auth_service
ENV PRIORITY=1

RUN apt-get update && \
    apt-get install -y python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /var/auth-api

COPY requirements.txt /var/auth-api/
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . /var/auth-api/

EXPOSE 8000

CMD ["gunicorn", "auth_service.wsgi:application", "--bind", "0.0.0.0:8000"]

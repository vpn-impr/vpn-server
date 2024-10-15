FROM python:3.12

WORKDIR /app

COPY ./requirements.txt ./

RUN pip install --upgrade pip && pip install -r /app/requirements.txt --no-cache-dir

COPY . ./

EXPOSE 8000

ENTRYPOINT ["sh", "/app/entrypoint.sh"]

CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:8000 core.web.asgi:application -w 1"]

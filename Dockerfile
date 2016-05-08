FROM python:3-alpine

COPY [".", "/app/src/"]

WORKDIR /app/src/
RUN pip install --no-cache-dir -r requirements.txt \
    && python manage.py migrate

ENV PYTHONUNBUFFERED="1"
EXPOSE 8080

CMD ["python", "manage.py", "runserver", "0.0.0.0:8080"]

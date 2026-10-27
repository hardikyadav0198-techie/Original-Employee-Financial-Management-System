
FROM python:3-alpine

WORKDIR /app

COPY . .

EXPOSE 8000

CMD ["python", "dashboard.py"]

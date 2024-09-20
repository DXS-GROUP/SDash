FROM python:3.11-slim

WORKDIR /app

EXPOSE 5000

COPY . .

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python3", "app/server.py"]

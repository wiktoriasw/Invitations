FROM python:3.13-alpine

WORKDIR /code

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["fastapi", "dev", "main.py", "--host", "0.0.0.0"]


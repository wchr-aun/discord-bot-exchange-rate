FROM python:3.10

WORKDIR /usr/src/app
COPY . .

RUN pip install --no-cache-dir --break-system-packages -r requirements.txt

CMD ["python", "./main.py"]

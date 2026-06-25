FROM python:3.14

WORKDIR /app
COPY . .
EXPOSE 5000

RUN pip install --no-cache-dir -r requirements.txt

ENV APP-SECRET-KEY="CoolSecretKey"

CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
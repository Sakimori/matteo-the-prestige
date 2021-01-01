FROM python:3.8
EXPOSE 5000

WORKDIR /app

COPY . ./
RUN pip install -r requirements.txt

CMD ["python", "the_presige.py"]

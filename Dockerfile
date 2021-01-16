# - Build stage 1: frontend (simmadome/ directory)
FROM node:alpine AS frontend
WORKDIR /app

COPY simmadome/package.json simmadome/package-lock.json ./
RUN npm install
COPY simmadome/ ./
RUN npm run build

# - Build stage 2: backend (Python)
FROM python:3.8
EXPOSE 5000
WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . ./
COPY --from=frontend /app/build/ simmadome/build/

CMD ["python", "the_prestige.py"]

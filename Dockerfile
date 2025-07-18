FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

COPY . .

RUN pip install -r requirements.txt
RUN pip install git+https://github.com/Patriotic20/sharq_models.git --no-cache-dir

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8082"]
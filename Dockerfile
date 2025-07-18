FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt
RUN pip install git+https://github.com/Patriotic20/sharq_models.git --no-cache-dir

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8082"]
FROM python:3.11-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends tesseract-ocr && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /streamlit_app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY streamlit_app.py .

EXPOSE 7860

CMD ["streamlit", "run", "streamlit_app.py", \
     "--server.port=7860", \
     "--server.address=0.0.0.0", \
     "--server.headless=true"]

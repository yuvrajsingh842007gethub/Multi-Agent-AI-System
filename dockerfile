FROM python:3.10-slim

WORKDIR /app

# System dependencies install karne ke liye
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

# Pura project container me copy karne ke liye
COPY . .

# Libraries install karne ke liye
RUN pip3 install --no-cache-dir -r requirements.txt

# Streamlit port expose karne ke liye
EXPOSE 8501

# App chalane ki command (app.py ke liye)
ENTRYPOINT ["python3", "-m", "streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]



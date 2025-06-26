
FROM python:3.10-slim
RUN apt-get update && apt-get install -y \
    wget unzip curl gnupg libnss3 libatk1.0-0 libatk-bridge2.0-0 \
    libcups2 libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 \
    libxrandr2 libgbm1 libgtk-3-0 xvfb && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -r requirements.txt && playwright install
CMD ["xvfb-run", "python3", "tiktok_register.py"]

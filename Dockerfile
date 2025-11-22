FROM debian:stable-slim

# ======================================================
# Cài các gói cần thiết + Chromium + ChromeDriver
# ======================================================
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    python3 \
    python3-pip \
    python3-venv \
    wget \
    curl \
    unzip \
    libglib2.0-0 \
    libgl1 \
    libnss3 \
    libxss1 \
    libxcomposite1 \
    libxcursor1 \
    libxi6 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libgtk-3-0 \
    libdrm2 \
    libxshmfence1 \
    libu2f-udev \
    libexpat1 \
    libxext6 \
    fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

# ======================================================
# Environment cho Chromium headless
# ======================================================
ENV CHROME_BIN="/usr/bin/chromium"
ENV CHROME_DRIVER="/usr/bin/chromedriver"
ENV DISPLAY=:99

# ======================================================
# WORKDIR
# ======================================================
WORKDIR /app

# Copy code
COPY . .

# Cài Python libs
RUN pip3 install --no-cache-dir -r requirements.txt

# ======================================================
# RUN BOT
# ======================================================
CMD ["python3", "bot.py"]

FROM python:3.10-slim

# Cài Chromium + ChromeDriver + dependencies
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    wget \
    curl \
    unzip \
    libglib2.0-0 \
    libgl1 \
    libgl1-mesa-dri \
    libnss3 \
    libxrender1 \
    libxi6 \
    libxext6 \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libatspi2.0-0 \
    libcups2 \
    libdrm2 \
    libgbm1 \
    libgtk-3-0 \
    libu2f-udev \
    libvulkan1 \
    libxcomposite1 \
    libxdamage1 \
    libxkbcommon0 \
    libxrandr2 \
    libxshmfence1 \
    fonts-liberation \
    xdg-utils \
    && rm -rf /var/lib/apt/lists/*

# WORKDIR
WORKDIR /app

# Copy code
COPY . .

# Install Python libs
RUN pip install --no-cache-dir -r requirements.txt

# Start
CMD ["python3", "bot.py"]

FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    xvfb \
    libnss3 \
    libgbm1 \
    libasound2t64 \
    chromium \
    chromium-driver \
    locales \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN echo "el_GR.UTF-8 UTF-8" > /etc/locale.gen && \
    locale-gen el_GR.UTF-8 && \
    update-locale LANG=el_GR.UTF-8

ENV LANG=el_GR.UTF-8
ENV LC_ALL=el_GR.UTF-8

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV DISPLAY=:99

CMD ["python","-u", "ergastirioV3.py"]

# Stage 1: Build nsjail
FROM debian:bookworm-slim AS nsjail-builder

RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    pkg-config \
    libnl-3-dev \
    libnl-route-3-dev \
    libprotobuf-dev \
    protobuf-compiler \
    flex \
    bison \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /tmp
RUN git clone https://github.com/google/nsjail.git
WORKDIR /tmp/nsjail
RUN make

# Stage 2: Runtime image
FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    libnl-3-200 \
    libnl-route-3-200 \
    libprotobuf32 \
    && rm -rf /var/lib/apt/lists/*


COPY --from=nsjail-builder /tmp/nsjail/nsjail /usr/local/bin/nsjail


COPY requirements.txt .
RUN python -m pip install --no-cache-dir -r requirements.txt


COPY app.py /app/app.py
COPY nsjail.cfg /app/nsjail.cfg
WORKDIR /app

EXPOSE 8080

CMD ["python", "app.py"]

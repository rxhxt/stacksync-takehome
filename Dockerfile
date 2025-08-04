# Stage 1: Build nsjail
FROM debian:bookworm-slim AS nsjail-builder

RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    git \
    make \
    pkg-config \
    flex \
    bison \
    libprotobuf-dev \
    protobuf-compiler \
    libnl-3-dev \
    libnl-genl-3-dev \
    libnl-route-3-dev \
    libcap2-bin \
    libcap-dev \
    libseccomp-dev \
    wget \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN git clone --depth 1 https://github.com/google/nsjail.git /tmp/nsjail && \
    cd /tmp/nsjail && \
    make

# Stage 2: Final image
FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    libprotobuf-dev \
    libnl-3-dev \
    libnl-genl-3-dev \
    libnl-route-3-dev \
    libcap2-bin \
    libcap-dev \
    libseccomp-dev \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy nsjail binary from builder
COPY --from=nsjail-builder /tmp/nsjail/nsjail /usr/local/bin/nsjail


COPY requirements.txt .
RUN python -m pip install --no-cache-dir -r requirements.txt


COPY . /app
WORKDIR /app

EXPOSE 8080



CMD ["python", "app.py"]

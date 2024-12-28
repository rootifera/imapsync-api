FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r /app/requirements.txt

RUN apt update && apt install -y \
    curl \
    libauthen-ntlm-perl \
    libcgi-pm-perl \
    libcrypt-openssl-rsa-perl \
    libdata-uniqid-perl \
    libencode-imaputf7-perl \
    libfile-copy-recursive-perl \
    libfile-tail-perl \
    libio-socket-inet6-perl \
    libio-socket-ssl-perl \
    libio-tee-perl \
    libhtml-parser-perl \
    libjson-webtoken-perl \
    libmail-imapclient-perl \
    libparse-recdescent-perl \
    libproc-processtable-perl \
    libmodule-scandeps-perl \
    libreadonly-perl \
    libregexp-common-perl \
    libsys-meminfo-perl \
    libterm-readkey-perl \
    libtest-mockobject-perl \
    libtest-pod-perl \
    libunicode-string-perl \
    liburi-perl \
    libwww-perl \
    libtest-nowarnings-perl \
    libtest-deep-perl \
    libtest-warn-perl \
    make \
    time \
    cpanminus \
    && rm -rf /var/lib/apt/lists/*

RUN curl -L https://raw.githubusercontent.com/imapsync/imapsync/master/imapsync -o /usr/local/bin/imapsync \
    && chmod +x /usr/local/bin/imapsync

COPY . /app

ENV PATH="/root/.local/bin:$PATH"

ENV REDIS_HOST=192.168.1.24

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8712"]

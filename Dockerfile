FROM ubuntu:jammy

RUN groupadd --gid 1001 devteam

# hadolint ignore=DL3059
RUN useradd -s /bin/bash -d /home/ffhm -m ffhm --gid 1001 --uid 1000
# COPY oceane_watcher.service /etc/systemd/system
# COPY swan_watcher.service /etc/systemd/system
# COPY cvp_watcher.service /etc/systemd/system
WORKDIR /home/ffhm

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Europe/Paris

# hadolint ignore=DL3008
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install --no-install-recommends -y python3-dev && \
    apt-get install --no-install-recommends -y libmysqlclient-dev && \
    apt-get install --no-install-recommends -y python3-pip && \
    apt-get install --no-install-recommends -y pkg-config && \
    apt-get install --no-install-recommends -y build-essential && \
    apt-get install --no-install-recommends -y sudo && \
    apt-get install --no-install-recommends -y cron && \
    apt-get install --no-install-recommends -y tzdata && \
    rm -rf /var/lib/apt/lists/*

RUN usermod -aG sudo ffhm && \
    echo "ffhm ALL=(ALL:ALL) NOPASSWD: ALL" >> /etc/sudoers

RUN touch /var/log/cron.log

USER ffhm
COPY ./requirements.txt .
COPY ./uwsgi.ini /home/ffhm

# hadolint ignore=DL3013
RUN pip install --no-cache-dir --requirement requirements.txt && \
    pip install --no-cache-dir pytz --upgrade && \
    pip install --no-cache-dir tzdata --upgrade && \
    pip install --no-cache-dir uwsgi

# Download base image ubuntu 22.04
FROM ubuntu:22.04

# LABEL about the custom image
LABEL maintainer="sasa@karanovic.ca"
LABEL version="0.2"
LABEL description="OpenFan UnRAID service for simple fan speed control based on UnRAID disk temperatures"
LABEL org.opencontainers.image.source=https://github.com/sasakaranovic/openfancontroller

# Disable Prompt During Packages Installation
ARG DEBIAN_FRONTEND=noninteractive

# Update Ubuntu Software repository
RUN apt update

# Install python from ubuntu repository
RUN apt install -y python3 python3-pip
RUN rm -rf /var/lib/apt/lists/*
RUN apt clean

# Copy all source files
ADD src /mnt/OpenFanService
ADD src/start.sh /mnt/OpenFanService

# Install python modules
RUN pip3 install -r /mnt/OpenFanService/requirements.txt

RUN ["chmod", "+x", "/mnt/OpenFanService/start.sh"]

# Run entrypoint
ENTRYPOINT ["/mnt/OpenFanService/start.sh"]

# Use official Python runtime as a parent image
FROM python:3.10.11

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        libssl-dev \
        zlib1g-dev \
        libbz2-dev \
        libreadline-dev \
        libsqlite3-dev \
        wget \
        curl \
        llvm \
        libncurses5-dev \
        libncursesw5-dev \
        xz-utils \
        tk-dev \
        libffi-dev \
        liblzma-dev && \
    rm -rf /var/lib/apt/lists/*

# Install Python 3.10.11 using virtualenv
RUN python3 -m venv .venv

# Set the working directory in the container
WORKDIR /code

# Copy the requirements file
COPY requirements.txt /code/

# Install project dependencies
RUN python3 -m pip install --no-cache-dir -r requirements.txt

# Copy the project code
COPY . /code/

# Command to run the application
CMD ["uvicorn", "main:app", "--host 0.0.0.0", "--port 8000", "--reload"]

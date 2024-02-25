# Use official Python runtime as a parent image
FROM python:3.10.11

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install pyenv
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
        liblzma-dev \
        python-openssl && \
    rm -rf /var/lib/apt/lists/*

RUN curl https://pyenv.run | bash

ENV PATH="/root/.pyenv/bin:${PATH}"

# Install Python 3.10.11 using pyenv
RUN pyenv install 3.10.11 && \
    pyenv global 3.10.11

# Install Poetry
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -
ENV PATH="/root/.poetry/bin:${PATH}"

# Set the working directory in the container
WORKDIR /code

# Copy the poetry files
COPY pyproject.toml poetry.lock /code/

# Install dependencies
RUN poetry install

# Copy the project code
COPY . /code/

# Command to run the application
CMD ["uvicorn", "main:app", "--reload"]

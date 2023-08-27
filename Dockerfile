FROM python:3-slim
ENV SETUPTOOLS_SCM_PRETEND_VERSION_FOR_RELNOTES 1.0.0
RUN apt-get update && apt-get install -y pandoc && rm -rf /var/lib/apt/lists/*

ADD . /app
WORKDIR /app

RUN pip install -e .

CMD ["python", "-m", "relnotes"]

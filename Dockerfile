FROM python:3 as build
RUN apt-get update && apt-get install -y pandoc && rm -rf /var/lib/apt/lists/*
ENV SETUPTOOLS_SCM_PRETEND_VERSION_FOR_RELNOTES 1.0.0

ADD . /app
WORKDIR /app

RUN pip wheel .

FROM python:3-slim
RUN --mount=type=bind,from=build,source=/app,target=/wheels pip install --no-index -f /wheels relnotes

CMD ["python", "-m", "relnotes"]

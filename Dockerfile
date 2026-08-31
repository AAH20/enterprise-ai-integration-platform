FROM python:3.13-slim AS build
WORKDIR /build
COPY pyproject.toml README.md ./
COPY src ./src
RUN pip wheel --no-cache-dir --wheel-dir /wheels .

FROM python:3.13-slim
RUN useradd --system --uid 10001 --create-home flowforge
WORKDIR /app
COPY --from=build /wheels /wheels
RUN pip install --no-cache-dir /wheels/* && rm -rf /wheels
RUN mkdir /data && chown flowforge:flowforge /data
USER 10001:10001
ENV FLOWFORGE_DB=/data/flowforge.db
EXPOSE 8080
ENTRYPOINT ["flowforge-api"]
CMD ["--port", "8080"]

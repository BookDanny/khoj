# syntax=docker/dockerfile:1
FROM ubuntu:jammy AS base
LABEL homepage="https://khoj.dev"
LABEL repository="https://github.com/khoj-ai/khoj"
LABEL org.opencontainers.image.source="https://github.com/khoj-ai/khoj"
LABEL org.opencontainers.image.description="Your second brain, containerized for personal, local deployment."

# Install System Dependencies
RUN apt update -y && apt -y install \
    python3-pip \
    swig \
    curl \
    # Required by RapidOCR
    libgl1 \
    libglx-mesa0 \
    libglib2.0-0 \
    # Required by llama-cpp-python pre-built wheels. See #1628
    musl-dev && \
    ln -s /usr/lib/x86_64-linux-musl/libc.so /lib/libc.musl-x86_64.so.1 && \
    # Clean up
    apt clean && rm -rf /var/lib/apt/lists/*

# Build Server
FROM base AS server-deps
WORKDIR /app
COPY pyproject.toml .
COPY README.md .
ARG VERSION=0.0.0
# use the pre-built llama-cpp-python, torch cpu wheel
ENV PIP_EXTRA_INDEX_URL="https://download.pytorch.org/whl/cpu https://abetlen.github.io/llama-cpp-python/whl/cpu"
# avoid downloading unused cuda specific python packages
ENV CUDA_VISIBLE_DEVICES=""
# 使用sed命令替换pyproject.toml文件中的版本号
RUN sed -i "s/dynamic = \\[\"version\"\\]/version = \"$VERSION\"/" pyproject.toml && \
    # 使用pip安装依赖，不使用缓存
    pip install --no-cache-dir .


# 这段代码是Dockerfile中的一个RUN指令，用于在构建Docker镜像时执行一个shell命令。具体来说，它使用`sed`命令来修改`pyproject.toml`文件中的内容。
# 1. `RUN`：这是一个Dockerfile指令，用于在构建镜像时执行一个命令。
# 2. `sed -i "s/dynamic = \\[\"version\"\\]/version = \"$VERSION\"/" pyproject.toml`：这是一个`sed`命令，用于在`pyproject.toml`文件中替换文本。`-i`选项表示直接修改文件，而不是输出到标准输出。`"s/dynamic = \\[\"version\"\\]/version = \"$VERSION\"/"`是`sed`命令的模式替换部分，它将`dynamic = ["version"]`替换为`version = "$VERSION"`。`$VERSION`是一个环境变量，它的值将在构建镜像时由Docker提供。
# 3. `&&`：这是一个逻辑与运算符，用于连接两个命令。只有当第一个命令成功执行（返回值为0）时，才会执行第二个命令。
# 4. `pip install --no-cache-dir .`：这是一个pip命令，用于安装Python依赖。`--no-cache-dir`选项表示不使用缓存目录，每次安装都会重新下载依赖。


# Build Web App
FROM node:20-alpine AS web-app
# Set build optimization env vars
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1
WORKDIR /app/src/interface/web
# Install dependencies first (cache layer)
COPY src/interface/web/package.json src/interface/web/yarn.lock ./
RUN yarn install --frozen-lockfile
# Copy source and build
COPY src/interface/web/. ./
RUN yarn build

# Merge the Server and Web App into a Single Image
FROM base
ENV PYTHONPATH=/app/src
WORKDIR /app
COPY --from=server-deps /usr/local/lib/python3.10/dist-packages /usr/local/lib/python3.10/dist-packages
COPY --from=web-app /app/src/interface/web/out ./src/khoj/interface/built
COPY . .
RUN cd src && python3 khoj/manage.py collectstatic --noinput

# Run the Application
# There are more arguments required for the application to run,
# but those should be passed in through the docker-compose.yml file.
# 定义一个变量PORT
ARG PORT
# 暴露端口
EXPOSE ${PORT}
# 设置容器启动时执行的命令
ENTRYPOINT ["python3", "src/khoj/main.py"]

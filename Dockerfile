FROM python:3.11-slim

# Update package list and set up mirrors
RUN apt-get update && \
    apt-get install -y apt-transport-https && \
    rm -rf /var/lib/apt/lists/* && \
    echo "deb https://mirrors.tuna.tsinghua.edu.cn/debian/ bullseye main contrib non-free" > /etc/apt/sources.list && \
    echo "deb https://mirrors.tuna.tsinghua.edu.cn/debian-security bullseye-security main contrib non-free" >> /etc/apt/sources.list && \
    apt-get update

WORKDIR /app

COPY requirements.txt .

# 使用清华大学 PyPI 镜像源安装依赖
RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
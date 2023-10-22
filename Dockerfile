# 使用一个Python基础镜像
FROM python:3.8-slim

# 设置工作目录
WORKDIR /app

# 复制应用文件到工作目录
COPY . /app

# 安装应用所需的依赖
RUN pip install -r requirements.txt

# 暴露应用运行的端口
EXPOSE 5000

# 启动应用
CMD ["python", "app.py"]

FROM python:3.10-slim

LABEL maintainer="huangxiaoye <huangxiaoye6@qq.com>"


COPY requirements.txt ./requirements.txt

RUN pip install --no-cache-dir --upgrade -r ./requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple && \
    pip install cryptography -i https://pypi.tuna.tsinghua.edu.cn/simple

# 复制目录
COPY ./ /agent

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

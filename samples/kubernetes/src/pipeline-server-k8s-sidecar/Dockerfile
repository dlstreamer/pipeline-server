FROM python:buster

COPY sidecar.py /app/sidecar.py
COPY requirements.txt /app/requirements.txt

RUN pip3 install -r /app/requirements.txt
ENV PYTHONUNBUFFERED=1
ENV PYTHONIOENCODING=UTF-8
CMD ["python3", "/app/sidecar.py"]

FROM python:3.11-slim

# Cài đặt Java cho PySpark
RUN apt-get update && apt-get install -y openjdk-11-jdk && rm -rf /var/lib/apt/lists/*
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
ENV PATH=$JAVA_HOME/bin:$PATH

# Cài đặt PySpark
RUN pip install --no-cache-dir pyspark==3.3.2

WORKDIR /app

# Copy và cài đặt requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ code
COPY . .

EXPOSE 5000
CMD ["python", "app2.py"]
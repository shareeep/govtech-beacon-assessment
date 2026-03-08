FROM docker.io/python:3.11-slim

WORKDIR /app

# Install Ansible + SSH client (for connecting to target servers)
RUN apt-get update && \
    apt-get install -y --no-install-recommends openssh-client sshpass && \
    rm -rf /var/lib/apt/lists/* && \
    pip install --no-cache-dir ansible

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY triage.py app.py eval.py ./
COPY templates/ templates/
COPY ansible/ ansible/
COPY start.sh .
RUN chmod +x start.sh

# Create results directory
RUN mkdir -p results/target

EXPOSE 5001
CMD ["./start.sh"]

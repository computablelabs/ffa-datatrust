FROM python:3.7-stretch

ARG accesskey
ARG secretkey

ENV AWS_ACCESS_KEY_ID=$accesskey
ENV AWS_SECRET_ACCESS_KEY=$secretkey

COPY . /app

# Configure flask app
WORKDIR /app
RUN pip install -i https://test.pypi.org/simple/ computable && \
    pip install -r requirements.txt

ENV FLASK_APP app.py
CMD ["python", "app.py"]

FROM python:3.7-stretch

COPY . /app

# Configure flask app
WORKDIR /app
RUN pip install -i https://test.pypi.org/simple/ computable && \
    pip install -r requirements.txt

ENV FLASK_APP app.py
CMD ["python", "app.py"]

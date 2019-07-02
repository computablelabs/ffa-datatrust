export
PYTHONPATH := .

test:
	FLASK_CONFIGURATION=test python -m pytest

run:
	# Start dev dynamodb with java -Djava.library.path=./DynamoDBLocal_lib -jar DynamoDBLocal.jar -sharedDb
	python app.py

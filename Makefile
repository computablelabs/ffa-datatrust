export
PYTHONPATH := .

test:
	FLASK_CONFIGURATION=test python -m pytest

run:
	# Start dev dynamodb with java -Djava.library.path=./DynamoDBLocal_lib -jar DynamoDBLocal.jar -sharedDb
	python app.py

run-docker:
	docker build -t ffa:local .
	docker run -p 5000:5000 ffa:local

local-docker:
	docker build -t ffa:local . -f Dockerfile_local.dockerfile \
		--build-arg accesskey=$(shell aws configure get aws_access_key_id) \
		--build-arg secretkey=$(shell aws configure get aws_secret_access_key)

docker-deploy:
	$(shell aws ecr get-login --no-include-email --region us-west-1)
	docker build -t computable/ffa:latest .
	docker tag computable/ffa:latest 365035671514.dkr.ecr.us-west-1.amazonaws.com/computable/ffa-api:latest
	docker push 365035671514.dkr.ecr.us-west-1.amazonaws.com/computable/ffa-api:latest

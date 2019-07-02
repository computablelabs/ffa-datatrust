# ffa-datatrust
Datatrust API for FFA

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

Python3. No support for python2 now, or ever.
Local running DynamoDB. Download [here](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/DynamoDBLocal.html)

### Installing

A step by step series of examples that tell you how to get a development env running

Create a virtual environment

```
python3 -m venv .env
```

Activate the virtual env

```
source .env/bin/activate
```

Install prerequisites via pip

```
pip install -r requirements.txt
```

Launch the API locally

```
make run
```

Verify operation + view swagger docs by browsing http://localhost:5000/api/

View the health of the API at http://localhost:5000/api/health/

## Running the tests

TODO


## Deployment

TODO

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/computablelabs/ffa-datatrust/tags). 

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details

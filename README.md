# Action
[![Build Status](https://travis-ci.org/Clacket/action.svg?branch=master)](https://travis-ci.org/Clacket/action) [![Documentation Status](https://readthedocs.org/projects/action/badge/?version=latest)](http://action.readthedocs.io/en/latest/?badge=latest)


The web app for Clacket.

## Install
1. Create a virtualenv (once) and activate it.
	```bash
	$ virtualenv -p python3 venv
	$ . venv/bin/activate
	```
2. Install the requirements.
	```bash
	$ make bootstrap
	```
3. Copy the .env file and fill it.
	```bash
	$ cp .env.example
	```

## Commands
- Run the server/app: `$ make run`
- Build the documentation: `$ make docs-build`
- Build & run the documentation locally: `$ make docs-run`
- Build Docker image: `$ make image-build`
- Test: `$ make test`

## Deployment
On merge to `master`, TravisCI runs tests, and if they're successful, it deploys the app with the required env vars to Elastic Beanstalk.

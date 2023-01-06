release: node_modules .pipenv lint bundle-python

lint:
	pipenv run black --line-length 79 serverless_fastapi
	pipenv run flake8 serverless_fastapi

clean: 
	find -name '*.pyc' | xargs rm -f
	find -name '__pycache__' | xargs rm -rf
	rm -rf cdk.out/
	rm -rf build-python/
	rm -rf .aws-sam/
	rm -f requirements.txt
	rm -f .deploy-dev-once
	rm -f sam-params.json
	rm -f .pipenv && pipenv --rm || true
	rm -f Pipfile.lock
	echo "Clean is finished"

.pipenv:
	pipenv lock
	pipenv sync -d
	touch "$@"

update-deps: clean
	pipenv update

build-python: .pipenv
	mkdir -p "$@"/
	echo "Building in $@/"
	pipenv requirements > requirements.txt
	pip install -r requirements.txt -t "$@/"
	# prune other trash
	find "$@/" -name "__pycache__" -type d | xargs rm -rf
	find "$@/" -name "*.pyc" -type d | xargs rm -rf
	rm -rf "$@/{_pytest}"

bundle-python: build-python
	echo "Copying local Python files"
	rsync -ah --exclude '*.pyc' serverless_fastapi  "build-python/"
	echo "The Python bundle's size: $$(du -sh "build-python/")"

pytest:
	pipenv run pytest -x

npmtest:
	npm run test

test: pytest npmtest

node_modules:
	npm install


deploy-dev: node_modules bundle-python
	cdk deploy -c stage=dev --outputs-file cdk.out/dev-stage-output.json
	
.deploy-dev-once: node_modules
	cdk deploy -c stage=dev --outputs-file cdk.out/dev-stage-output.json
	touch $@

deploy-staging: release
	cdk deploy -c stage=staging

deploy-prod: release
	cdk deploy -c stage=prod

synth-dev: node_modules
	cdk synth -c stage=dev

.PHONY = clean run-flask bundle-python test pytest npmtest \
	sam-local deploy-dev deploy-staging deploy-prod release  \
	update-deps synth-dev npm-install lint
	
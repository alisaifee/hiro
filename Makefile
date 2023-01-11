lint:
	black --check hiro tests
	flake8 hiro tests

lint-fix:
	black tests hiro
	isort -r --profile=black tests hiro
	autoflake8 -i -r tests hiro

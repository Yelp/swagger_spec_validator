.PHONY: docs test clean

test:
	tox

docs:
	tox -e docs

clean:
	find . -name '*.pyc' -delete
	rm -rf swagger_validator.egg-info
	rm -rf docs/build
	rm -f MANIFEST

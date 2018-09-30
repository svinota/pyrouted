
clean:
	rm -rf dist
	rm -rf build
	rm -f MANIFEST

dist:
	python setup.py sdist

upload: dist
	python -m twine upload --repository-url https://upload.pypi.org/legacy/ dist/*

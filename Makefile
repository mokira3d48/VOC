venv:
	python3 -m venv env

install:
	python3 --version
	pip install --upgrade pip
	pip install torch torchvision --index-url "https://download.pytorch.org/whl/cpu" && \
	pip install -r requirements.txt

gpu_install:
	python3 --version
	pip install --upgrade pip
	pip install torch torchvision && \
	pip install -r requirements.txt

dev:
	pip install -e .

test:
	pytest tests

run:
	python3 -m voc

pep8:
	# Don't remove their commented follwing command lines:
    # autopep8 --in-place --aggressive --aggressive --recursive .
    # autopep8 --in-place --aggressive --aggressive example.py


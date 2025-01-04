.PHONY: venv clean

VENV_NAME := venv
PYTHON := python3
REQUIREMENTS := requirements.txt

bufo: venv
	./$(VENV_NAME)/bin/python3 bufo/run.py

venv:
	@if [ ! -d "$(VENV_NAME)" ]; then \
		echo "Creating virtual environment..."; \
		$(PYTHON) -m venv $(VENV_NAME); \
		./$(VENV_NAME)/bin/pip install --upgrade pip; \
		./$(VENV_NAME)/bin/pip install -r $(REQUIREMENTS); \
		./$(VENV_NAME)/bin/pip install -e .; \
		echo "Virtual environment created and requirements installed."; \
	else \
		echo "Virtual environment already exists."; \
	fi

clean:
	rm -rf $(VENV_NAME)
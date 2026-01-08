.PHONY: test unit_tests integration_tests help

# Define the virtual environment directory
VENV := venv

# Target to run all tests
test: unit_tests integration_tests

# Target to install dependencies and set up the environment
install:
	@echo "Setting up virtual environment and installing dependencies..."
	@python3 -m venv $(VENV)
	. $(VENV)/bin/activate && pip install --upgrade pip
	. $(VENV)/bin/activate && pip install -r requirements.txt

# Target to run unit tests
# Defaults to looking for files that match the pattern test*.py
unit_tests:
	@echo "Running unit tests..."
	. $(VENV)/bin/activate && python3 -m unittest discover -s test/unit_tests
#   . $(VENV)/bin/activate && coverage report -m

# Target to run integration tests
# integration_tests:
# 	@echo "Running integration tests..."
# 	@python -m unittest discover -s test/integration_tests\
#   @coverage report -m

# Target to generate an HTML code coverage report for all tests
#coverage:
#	@echo "Running all tests with coverage and generating HTML report..."
#	. $(VENV)/bin/activate && coverage run -m unittest discover -s test  
#	. $(VENV)/bin/activate && coverage report -m
#	. $(VENV)/bin/activate && coverage html
#	@echo "HTML coverage report generated in the 'htmlcov' directory."

# Clean up coverage files
#clean:
#	@echo "Cleaning up coverage files..."
#	@rm -rf .coverage htmlcov

# Define a help target to display available targets
help:
	@echo "Available targets:"
	@echo "  test               - Run all tests (unit and integration)"
	@echo "  unit_tests         - Run unit tests"
	@echo "  help               - Display this help message"
	@echo "  coverage           - Generate a code coverage report"
	@echo "  clean              - Clean up generated coverage files"
# @echo "  integration_tests  - Run integration tests"

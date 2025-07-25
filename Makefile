# TaaP POC GitHub - Makefile for project management

.PHONY: help install test test-fast test-verbose clean coverage lint format docs docker-build docker-run

# Default target
help:
	@echo "TaaP POC GitHub - Available commands:"
	@echo ""
	@echo "Setup and Installation:"
	@echo "  install       Install all dependencies"
	@echo "  install-dev   Install development dependencies"
	@echo ""
	@echo "Testing:"
	@echo "  test          Run all tests"
	@echo "  test-fast     Run tests in parallel"
	@echo "  test-verbose  Run tests with verbose output"
	@echo "  test-api      Run API tests only"
	@echo "  test-container Run container tests only"
	@echo "  test-db       Run database tests only"
	@echo "  test-config   Run configuration tests only"
	@echo "  test-network  Run network tests only"
	@echo "  test-security Run security tests only"
	@echo "  test-perf     Run performance tests only"
	@echo ""
	@echo "Quality and Reports:"
	@echo "  coverage      Generate coverage report"
	@echo "  lint          Run code linting"
	@echo "  format        Format code with black"
	@echo "  docs          Generate documentation"
	@echo ""
	@echo "Cleanup:"
	@echo "  clean         Clean up generated files"
	@echo "  clean-cache   Clean Python cache files"
	@echo ""
	@echo "Docker:"
	@echo "  docker-build  Build Docker image"
	@echo "  docker-run    Run tests in Docker container"

# Installation
install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements.txt
	pip install black flake8 mypy pre-commit

# Testing
test:
	pytest

test-fast:
	pytest -n auto

test-verbose:
	pytest -v -s

test-api:
	pytest -m api

test-container:
	pytest -m container

test-db:
	pytest -m database

test-config:
	pytest -m unit

test-network:
	pytest -m network

test-security:
	pytest -m security

test-perf:
	pytest -m performance

# Quality and Reports
coverage:
	pytest --cov=src --cov-report=html --cov-report=term-missing
	@echo "Coverage report generated in htmlcov/index.html"

lint:
	flake8 src tests
	mypy src

format:
	black src tests

docs:
	@echo "Generating documentation..."
	@mkdir -p docs
	@echo "# TaaP POC Documentation" > docs/README.md
	@echo "Documentation generated in docs/"

# Cleanup
clean:
	rm -rf reports/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .pytest_cache/
	rm -rf __pycache__/
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

clean-cache:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache/

# Docker
docker-build:
	docker build -t taap-poc-github .

docker-run:
	docker run --rm -v $(PWD):/app taap-poc-github

# Environment setup
setup-env:
	@echo "Setting up environment variables..."
	@echo "export DB_HOST=localhost" >> .env
	@echo "export DB_PORT=5432" >> .env
	@echo "export REDIS_HOST=localhost" >> .env
	@echo "export REDIS_PORT=6379" >> .env
	@echo "export API_BASE_URL=http://localhost:8080" >> .env
	@echo "Environment file created: .env"

# Development workflow
dev-setup: install-dev setup-env
	pre-commit install
	@echo "Development environment setup complete!"

# Full test suite with reports
test-all: clean
	pytest --cov=src --cov-report=html --cov-report=xml --html=reports/report.html --self-contained-html
	@echo "Full test suite completed with reports"
	@echo "HTML report: reports/report.html"
	@echo "Coverage report: htmlcov/index.html"

# CI/CD simulation
ci-test:
	pytest --cov=src --cov-report=xml --junitxml=junit.xml
	@echo "CI test completed - results in junit.xml and coverage.xml"

# Performance benchmarking
benchmark:
	pytest -m performance --benchmark-only
	@echo "Performance benchmarks completed"

# Security scanning
security-scan:
	pytest -m security -v
	@echo "Security tests completed"

# Generate test matrix
test-matrix:
	@echo "Running test matrix across different configurations..."
	pytest -m "not slow" --tb=short
	@echo "Quick test matrix completed"

# Database setup (if needed)
setup-db:
	@echo "Setting up test database..."
	# Add database setup commands here
	@echo "Database setup completed"

# Kubernetes testing
test-k8s:
	pytest -m container -k kubernetes
	@echo "Kubernetes tests completed"

# API integration tests
test-integration:
	pytest -m integration
	@echo "Integration tests completed"

# Load testing
load-test:
	pytest -m performance -k "load" -v
	@echo "Load tests completed" 
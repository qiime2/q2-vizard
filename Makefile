.PHONY: all lint test test-cov install dev clean distclean

PYTHON ?= python

all: ;

lint:
	q2lint
	flake8

test: all
	py.test

test-cov: all
	py.test --cov=q2_vizard

install: all
	$(PYTHON) -m build --wheel

dev: all
	pip install -e .

clean: distclean

distclean: ;

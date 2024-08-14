.PHONY: all lint test test-cov install dev clean distclean

all: ;

lint:
	q2lint
	flake8

test: all
	py.test

test-cov: all
	py.test --cov=q2_vizard

install: all
	pip install --dry-run --report report.json . && cat report.json && pip install --debug -v .

dev: all
	pip install -e .

clean: distclean

distclean: ;

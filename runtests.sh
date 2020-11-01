#!/bin/sh
# Run all tests and generate coverage report

coverage run --source arpeggio -m py.test arpeggio/tests || exit 1
coverage report --fail-under 90 || exit 1
# Run this to generate html report
# coverage html --directory=coverage
#flake8 || exit 1

#!/bin/sh
COVERAGE=venv/bin/coverage

$COVERAGE erase
$COVERAGE run -m unittest discover
$COVERAGE report
$COVERAGE html

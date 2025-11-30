#!/bin/bash
export PYTHONPATH=$PYTHONPATH:$(pwd)
coverage run -m pytest target_repo/tests
RET=$?
if [ $RET -ne 0 ]; then
    exit $RET
fi
coverage xml
RET=$?
if [ $RET -ne 0 ]; then
    exit $RET
fi
coverage report -m
exit 0

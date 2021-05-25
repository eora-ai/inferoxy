#!/bin/sh

if [ $1 = "TEST" ]; then
  pytest task_manager
  pytest batch_manager
  pytest debatch_manager
  pytest zmq_bridge
  pytest grpc_bridge
  pytest restapi_bridge
  pytest model_storage
  pytest bridge_config_parser
elif [ $1 = "COVERAGE" ]; then
  COVERAGE_FILE=.coverage.task_manager coverage run -m pytest task_manager 2>&1 1>/dev/null 
  COVERAGE_FILE=.coverage.batch_manager coverage run -m pytest batch_manager 2>&1 1>/dev/null 
  COVERAGE_FILE=.coverage.debatch_manager coverage run -m pytest debatch_manager 2>&1 1>/dev/null 
  COVERAGE_FILE=.coverage.zmq_bridge coverage run -m pytest zmq_bridge 2>&1 1>/dev/null 
  COVERAGE_FILE=.coverage.grpc_bridge coverage run -m pytest grpc_bridge 2>&1 1>/dev/null 
  COVERAGE_FILE=.coverage.restapi_bridge coverage run -m pytest restapi_bridge 2>&1 1>/dev/null 
  COVERAGE_FILE=.coverage.model_storage coverage run -m pytest model_storage 2>&1 1>/dev/null 
  COVERAGE_FILE=.coverage.bridge_config_parser coverage run -m pytest bridge_config_parser 2>&1 1>/dev/null 
  coverage combine .coverage.task_manager .coverage.batch_manager .coverage.debatch_manager .coverage.zmq_bridge .coverage.grpc_bridge .coverage.restapi_bridge .coverage.model_storage .coverage.bridge_config_parser
  coverage report --omit="venv/*"
else
  cd bridge_config_parser
  python3 main.py
  cd ../
  /usr/bin/supervisord -c /etc/supervisor/supervisord.conf
fi


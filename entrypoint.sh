#!/bin/sh

cd bridge_config_parser
python3 main.py
cd ../
/usr/bin/supervisord -c /etc/supervisor/supervisord.conf


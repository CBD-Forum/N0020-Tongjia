#!/bin/bash

# override nginx config
cp nginx.conf /etc/nginx/conf.d/

# add related python libs
pip install -r requirement.txt

# refresh nodejs libs
bash frontend/install_frontend.sh
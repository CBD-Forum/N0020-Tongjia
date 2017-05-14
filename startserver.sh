#!/bin/bash

#cp nginx/nginx.conf /etc/nginx/nginx.conf
cp nginx.conf /etc/nginx/conf.d/
# init file

echo "start redis"
# start redis
redis-server --daemonize yes

#echo ""
#echo "==========="
#echo "start queue"
#echo "start message queue"
#nohup python /app/deamonqueue.py &
#echo "start match queue"
#nohup python /app/queue/cny2btcQ.py &
#nohup python /app/queue/cny2goldQ.py &
#nohup python /app/queue/gold2btcQ.py &

echo ""
echo "==========="
echo "start mongo"
# start mongodb
mongod --fork --logpath /var/log/mongod.log

echo ""
echo "==========="
echo "start uwsgi"
# start uwsgi
uwsgi /app/config.ini

echo ""
echo "==========="
echo "start nginx"
# start server
nginx

#echo ""
#echo "==========="
#echo "start front-end server"
#bash frontend/start_front_server.sh
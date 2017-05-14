#!/bin/bash

echo "start redis"
# start redis
redis-server --daemonize yes

#echo ''
#echo "start queue"
#echo "start message queue"
#nohup python /app/deamonqueue.py &
#echo "start match queue"
#nohup python /app/queue/cny2btcQ.py &
#nohup python /app/queue/cny2goldQ.py &
#nohup python /app/queue/gold2btcQ.py &

echo ''
echo "start mongo"
# start mongodb
mongod --fork --logpath /var/log/mongod.log

echo ''
echo "start node"
# TODO

echo ''
echo "start server"
# start server
python manage.py runserver -h 0.0.0.0

FROM tiangolo/uwsgi-nginx:latest

MAINTAINER Sebastian Ramirez <tiangolo@gmail.com>

# change to local
ENV TZ=Asia/Shanghai
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Add app configuration to Nginx
# TODO check as nginx deamon
# COPY nginx/nginx.conf /etc/nginx/nginx.conf
COPY nginx.conf /etc/nginx/conf.d/

# install redis and start
COPY redis-install.sh /tmp/
RUN chmod +x /tmp/redis-install.sh
RUN /bin/bash /tmp/redis-install.sh

COPY startserver.sh /tmp/
RUN chmod +x /tmp/startserver.sh

# front end
RUN apt-get install -y curl
RUN curl -sL https://deb.nodesource.com/setup_6.x | bash -
RUN apt-get install -y nodejs

RUN dpkg-divert --local --rename --add /etc/init.d/mongod
RUN ln -s /bin/true /etc/init.d/mongod
## Import MongoDB public GPG key AND create a MongoDB list file
RUN apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 7F0CEB10
RUN echo 'deb http://downloads-distro.mongodb.org/repo/ubuntu-upstart dist 10gen' | tee /etc/apt/sources.list.d/10gen.list
RUN apt-get update

# install mongodb
# Create the MongoDB data directory
RUN mkdir -p /data/db
RUN apt-get install -y apt-utils
RUN apt-get install -y mongodb-org

COPY requirement.txt /tmp/
RUN pip install -r /tmp/requirement.txt

#RUN frontend/install_frontend.sh init

ENTRYPOINT ["/bin/bash"]

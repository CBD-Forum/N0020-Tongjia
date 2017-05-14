\# 根据dockerfile 构建镜像
```
docker build -t debug .
```

\# build init image  对拉取好的镜像添加inittag
```
docker tag <image id> debug:init
```

\# 运行这个镜像, 注意至少开启 5000 8000 端口，5000是给python自带的服务器使用的，8000是给nginx使用的
```
docker run -v <你电脑上的该项目的根目录>:/app -p 5000:5000 -p 8000:8000 -p 8001:8001 -it --entrypoint=/bin/bash debug:init
# 例如:
docker run -v B:\projects\python\PyCharm\PartTimeJobPlatform:/app -p 5000:5000 -p 8000:8000 -p 8001:8001 -it --entrypoint=/bin/bash debug:init
```

\#进入到容器的镜像后，运行 startserver.sh 可以启动 nginx服务(占据8000端口)
>:/app# ./startserver.sh

\# 或者可单独启动 python 服务器(占据5000端口)
>:/app# python manage.py runserver -h 0.0.0.0


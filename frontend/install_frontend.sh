#!/bin/bash

init=$1
echo $init

cd `dirname $0`

dir_root='PartTimePlatform-frontend'
dir_cur=`pwd`

dir_cur=$dir_cur"/"$dir_root

echo "current dir: "$dir_cur
cd $dir_cur

# install dependecies
echo "npm install"
npm install
# pacakge to deploy
echo "npm build"
npm run build

if [ "$init" == "init" ]; then
    echo 'init install http-server'
    # enter the root directory
    cd dist
    # install node http-server
    npm install -g http-server
fi


echo 'finish'
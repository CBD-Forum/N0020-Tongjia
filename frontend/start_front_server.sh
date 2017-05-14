#!/bin/bash

cd `dirname $0`

dir_root='PartTimePlatform-frontend'
dir_cur=`pwd`

dir_cur=$dir_cur"/"$dir_root"/dist"

echo "current dir: "$dir_cur
cd $dir_cur

# deploy
hs -p 8080
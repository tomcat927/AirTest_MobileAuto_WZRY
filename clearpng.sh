#!/usr/bin/env bash
#.pngtmp作为备用目录,以及活动更新图片目录,不参与仓库同步
if [ ! -d .pngtmp ]; then mkdir -p .pngtmp; fi
mv assets/* .pngtmp/
for i in $(grep -Eo 'tpl[[:alnum:]_]*.png' wzry.py) $(grep -Eo 'tpl[[:alnum:]_]*.png' wzyd.py)
do
cp .pngtmp/$i assets/
#echo cp .pngtmp/* .
done
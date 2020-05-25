#!/bin/bash
set -e
set -x

MUSIC_PATH=${ICECAST_URL}

while [ `pgrep -x ffmpeg` ]
do
meta=`ffprobe -v error -show_format "$MUSIC_PATH" | grep StreamTitle | cut -d= -f2`
case "$meta" in
     *\ -\ *) artist=`echo $meta|cut -d- -f1`;title=`echo $meta|sed "s/$artist-\ //"`;echo $title>/tmp/title;echo $artist>/tmp/artist;;
     *) echo $meta>/tmp/title;echo >/tmp/artist;;
esac
sleep 5
done

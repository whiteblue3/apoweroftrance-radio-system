#!/bin/bash
set -e
set -x

nohup /scripts/live-meta.sh &

echo -e ${CHANNEL} > /tmp/channel

echo artist > /tmp/artist
echo title > /tmp/title

ffmpeg -f image2 -stream_loop -1 -re -loop 1 -i /srv/apoweroftrance.png -i ${ICECAST_URL} \
-vcodec libx264 -r 59.94 -force_key_frames "expr:gte(t,n_forced*2)" -preset ultrafast -profile:v high -tune:v zerolatency \
-acodec libmp3lame -vbr 5 \
-filter_complex "
[1:a]showwaves=mode=cline:s=qqvga:colors=White@1.0:scale=lin[v1];
[0:v][v1]overlay=(1920-160)/2:1080-50-36-120-4,drawtext=textfile='/tmp/channel':fontfile=/srv/Fatsans.ttf:fontcolor=White@1.0:fontsize=48:shadowcolor=black:shadowx=2:shadowy=2:x=30:y=30,
drawtext=textfile=/tmp/title:reload=1:fontfile=/srv/NanumGothicBold.ttf:fontcolor=White@1.0:fontsize=36:shadowcolor=black:shadowx=2:shadowy=2:x=30:y=1080-50-36,
drawtext=textfile=/tmp/artist:reload=1:fontfile=/srv/NanumGothicBold.ttf:fontcolor=White@1.0:fontsize=24:shadowcolor=black:shadowx=2:shadowy=2:x=30:y=1080-50-36-24-4
[out]" \
-map [out] -map 1:a -pix_fmt yuv420p -c:a copy -r:a 44100 \
-f flv ${YOUTUBE_URL}

exec "$@"

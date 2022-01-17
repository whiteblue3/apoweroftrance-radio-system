FROM jrottenberg/ffmpeg:latest
MAINTAINER @whiteblue3 https://github.com/whiteblue3

COPY ./apoweroftrance.png /srv/apoweroftrance.png
COPY ./startup.sh /scripts/startup.sh
COPY ./live-meta.sh /scripts/live-meta.sh
COPY ./Fatsans.ttf /srv/Fatsans.ttf
COPY ./NanumGothic.ttf /srv/NanumGothic.ttf
COPY ./NanumGothicBold.ttf /srv/NanumGothicBold.ttf

ENV ICECAST_URL "https://listen.apoweroftrance.com/yui"
ENV CHANNEL "A Power of Trance\nCH.YUI"
ENV STREAM_URL "rtmp://a.rtmp.youtube.com/live2/52my-hved-tvpe-r0t3-fb6e"

ENTRYPOINT ["/scripts/startup.sh"]

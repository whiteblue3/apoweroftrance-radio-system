Music Daemon is server-side software for streaming radio

# Install Pre-Requirements
You must install libshout on your system.

Windows does not support currently.

## Mac OS X
run code in terminal

    ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)" < /dev/null 2> /dev/null
    brew install libshout

## Ubuntu

    sudo apt install libshout3

# Install

    pip3 install -r requirement.txt

# TODO
- [ ] AAC 지원
- [ ] Google Cloud Storage 마운트


# Config
여기서는 config.ini 의 설정에 대해 설명합니다

    [daemon]
    musicdaemon = yui, alice, miku
    server = server

데몬 설정입니다.
musicdaemon: 단순한 데몬의 이름들입니다만 실제 IceCast2 에 마운트될 마운트 포인트로 사용됩니다.
server: 외부에서 데몬을 컨트롤할 http 서버의 이름입니다. 무난하게 server 라고 입력하면 됩니다

    [icecast2_yui]
    host = 127.0.0.1
    port = 8000
    mount = yui
    user = source
    password = hackme
    codec = mp3
    name = A Power of Trance CH.YUI
    genre = Trance
    bitrate = 128000
    samplerate = 44100
    url =

IceCast2의 설정입니다. 섹션 이름은 icecast2_데몬이름 의 형식을 취해야 하며 데몬 섹션에서 나열한 데몬이름과 일치해야합니다

    [callback_yui]
    on_startup = https://r3xgeyodxb.execute-api.ap-northeast-2.amazonaws.com/test
    on_play = https://ezlzag93l0.execute-api.ap-northeast-2.amazonaws.com/test
    on_stop = https://rnw46ry881.execute-api.ap-northeast-2.amazonaws.com/test

데몬과 연계하는 콜백입니다

on_startup 에서는 데몬이 시작될때 호출되며, 최초의 플레이 리스트를 셋팅하는데 사용됩니다

on_play 에서는 플레이가 시작될때 호출되며, 외부 서비스에서 재생관련 통계를 위해 보통 사용됩니다.

on_stop 에서는 플레이가 종료될때 호출되며, 다음 곡을 Queue-In 할때 사용합니다


on_startup과 on_stop은 GET으로 호출되며 파라미터는 url-path에 포함되거나 ? Query-String 형식으로 표현되며 보통 데몬 이름이 사용됩니다

on_play는 POST 로 호출되며 파라미터는 JSON 규격으로 사용됩니다.

# Command Set of MusicDaemon
뮤직데몬은 자체적인 커맨드를 받아 실행할 REST 규격의 인터페이스가 존재합니다
GET과 POST로 나뉘어 있으며 GET은 현재 데몬의 상태를 조회하는데 사용되고, POST는 플레이리스트를 Queue-In 하는데 사용됩니다

GET 호출형식: http://127.0.0.1:9000/yui

yui는 데몬이름입니다.


POST 호출형식은 아래의 JSON을 사용합니다

    {
        "host": "server",
        "target": "yui",
        "command": "queue",
        "data": {
            "id": 0,
            "location": "/Users/whiteblue3/Documents/dev/projects/apoweroftrance.com/source/radio/volumes/demo.mp3",
            "artist": "MOBIUS",
            "title": "Trance Template"
        }
    }
    
- host는 대개 http 서버 인터페이스인 server 가 무난하며 고정형식입니다.
- target은 명령을 수행할 뮤직데몬의 이름입니다
- command는 queue, unqueue, setlist의 3가지이며, 각각 queue-in (곡추가), queue-out (플레이리스트에서 곡 제거), 플레이리스트 덮어쓰기입니다.

data는 unqueue의 경우 아래의 형식입니다

    "data": {
        "index_at": 0
    }

플레이리스트에서 해당 인덱스의 곡을 제거한다는 의미입니다

queue와 setlist는 아래의 형식을 사용하며 차이는 배열 [] 이냐 아니냐의 차이입니다


    "data": {
        "id": 0,
        "location": "/Users/whiteblue3/Documents/dev/projects/apoweroftrance.com/source/radio/volumes/demo.mp3",
        "artist": "MOBIUS",
        "title": "Trance Template"
    }
    
- id값은 서비스에서 해당 곡의 곡ID 정도가 될수 있습니다.
- location값은 실제 뮤직데몬이 참조할 시스템 내에서의 곡파일 위치입니다
- artist는 작곡가 혹은 아티스트명입니다
- title은 곡의 제목입니다


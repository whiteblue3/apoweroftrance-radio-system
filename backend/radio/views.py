from django.shortcuts import render


"""
Namespace: radio

Required API
- GET track: 모든 서비스중인 트랙. 페이징 처리 필요. AllowAny
- GET track/{track_id}: 특정 곡에 대한 정보 조회. AllowAny
- POST track: 신규 트랙 업로드
- DELETE track/{track_id}: 트랙 삭제. 플레이큐에서도 제거. 뮤직데몬에도 반영
- POST like/{track_id}: 사용자가 특정 트랙을 좋아요, 싫어요 및 해제
- GET playqueue: 현재 플레이 리스트 조회. 페이징 처리 필요. AllowAny

Admin/Staff ONLY
- POST playqueue/reset: 현재 플레이 리스트를 리셋. 관리자 기능
- POST queuein/{track_id}: 플레이리스트에 곡추가. 관리자 기능
- DELETE unqueue/{index}: 지정된 현재 플레이리스트의 인덱스의 곡을 플레이리스트에서 제거, 관리자 기능

Required Callback
- GET on_startup/{channel}: 서비스 구동시 최초의 플레이 리스트 셋업
- POST on_play/{channel}: 플레이 History 기록 
- GET on_stop/{channel}: 새로운 곡을 플레이 리스트에 queuein
"""
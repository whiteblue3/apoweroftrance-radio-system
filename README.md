
A Power of Trance 방송 서버입니다. 뮤직 데몬과 API 서버로 구성되어있습니다.
이 프로젝트는 오픈소스로 공개되어있으며 GPL 라이선스를 따릅니다.

# 서버 스펙
- 플랫폼: Docker or Kubernetes
- 데이터베이스: PostgreSQL 11 이상

# musicdaemon
ICECAST 서버로 실제 방송을 내보내는 데몬입니다.

- 데몬 본체
- 데몬 컨트롤용 HTTP 서버

로 구성되어있으며, API 서버와 분리해서 단독으로도 동작하도록 설계되어있습니다.


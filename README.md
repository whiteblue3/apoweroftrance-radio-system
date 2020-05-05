A Power of Trance is audio broadcasting server. 
It contains musicdaemon and API server.
This project is published as opensource and use GPLv3 license.

# Server Spec
- Platform: Docker or Kubernetes
- Database: PostgreSQL 11 over
- Python: 3.6
- Storage: Google Cloud Storage
- Nginx: latest
- Icecast: 2.4.4
- WSGI: uWSGI 2.0.18

for design as microservices, all microservice use same database

# musicdaemon
Real broadcast daemon to stream icecast2.
It contains

- daemon body
- HTTP control server for daemon

And it's designed for run as a standalone mode.

# TODO
- [x] Search Music and User Nickname
- [ ] Access Logging with DJango Login
- [ ] Deploy to Kubernetes
- [ ] Support AWS S3
- [ ] Streaming with YouTube
- [ ] Auto Beat Matching
- [ ] Layer with Ment while playing (Voice Composition)

# Radio Backend Environment Variable
See backend/Dockerfile.

These variables is basic setup

    ENV NGINX=127.0.0.1:80
    ENV GOOGLE_APPLICATION_CREDENTIALS /etc/gcloud/service-account-key.json
    ENV DJANGO_SETTINGS_MODULE=app.settings
    
These variables works with uwsgi

    ENV UWSGI_WSGI_FILE=/backend/app/wsgi.py
    ENV UWSGI_SOCKET=0.0.0.0:8090 
    ENV UWSGI_CHMOD_SOCKET=644
    ENV UWSGI_LAZY_APPS=1 
    ENV UWSGI_WSGI_ENV_BEHAVIOR=holy 
    ENV UWSGI_POST_BUFFERING=1
    ENV UWSGI_MASTER=1 
    ENV UWSGI_HTTP_AUTO_CHUNKED=1 
    ENV UWSGI_HTTP_KEEPALIVE=1 
    ENV UWSGI_PROCESS=4
    ENV UWSGI_STATIC_MAP="/static/=/backend/.static/" 
    ENV UWSGI_STATIC_EXPIRES_URI="/static/.*\.[a-f0-9]{12,}\.(css|js|png|jpg|jpeg|gif|ico|woff|ttf|otf|svg|scss|map|txt) 315360000"
    
This variable define like 'dev', 'stage', 'production'

    ENV STAGE 'dev'

You must define these variables because secret information.

    ENV SECRET_KEY = ''
    ENV JWT_SECRET_KEY = ''
    ENV AES_KEY = ''
    ENV AES_SECRET = ''
    ENV EMAIL_HOST_USER = ''
    ENV EMAIL_HOST_PASSWORD = ''
    
    ENV DB_NAME 'radio'
    ENV DB_HOST '127.0.0.1'
    ENV DB_USERNAME 'postgres'
    ENV DB_PASSWORD ''
    ENV DB_PORT 5432
    
    ENV REDIS_URL "127.0.0.1"
    ENV REDIS_PORT 6379
    ENV REDIS_DB 0


A Power of Trance is audio broadcasting server. 
It contains musicdaemon and API server.
This project is published as opensource and use LGPL license.

# Donation
A Power of Trance is an open source driven project. We receive sponsor for server maintenance and management through PayPal, and also receive sponsor by cryptocurrencies such as Bitcoin and Ethereum.
- PayPal : preparing
- Bitcoin : bc1q49aq0ktmaa6n0qxq4787xw3k7uwl09q2vtf0ts
- Ethereum : 0x8b08bDa86d54F0ED51A04E60279C53F99f6ddF40

# Deploy Issue
If you use PyCharm and before code push, first you must select file README.md and commit, push code. This is a PyCharm bug.

# Server Spec
- Platform: Docker Compose (Local Dev) or Kubernetes (Production)
- Database: PostgreSQL 11 over
- Python: 3.6
- Storage: Google Cloud Storage
- Nginx: latest (unprivileged version)
- Icecast: 2.4.4
- WSGI: uWSGI 2.0.18

for design as microservices, all microservice use same database

# Pre-Requirements for Running Server
You NEVER, DO NOT share these files anywhere!

This system running on Google Kubernetes Engine. 
So, You need to acquire Google OAuth2 secret json

- Google OAuth2 Secret Json File (You NEVER, DO NOT share this file anywhere!)
- Create file secret.json under project root and fill this fields


```
// secret.json
// You NEVER, DO NOT share these secret.json file anywhere!
{
    "SECRET_KEY": <DJango Secret Key>,
    "JWT_SECRET_KEY": <JWT Secret Key>,
    "AES_KEY": <32bit AES 256 KEY>,
    "AES_SECRET": <16bit AES 256 Initial IV>,
    "EMAIL_HOST_USER": <System Email Sender Address>,
    "EMAIL_HOST_PASSWORD": <System Email Sender Password>,
    "GCP_PROJECT_ID": <Google Project ID>,
    "GCP_STORAGE_BUCKET_NAME": <Public Access Media Bucket Name of Google Storage>,
    "GS_BUCKET_NAME": <Public Access Static File Bucket Name of Google Storage>
}
```

- Prepare this secret.json for account, admin, radio, upload, post 
- These file name define like account_secret.json, admin_secret.json, 
  radio_secret.json, post_secret.json, upload_secret.json.
- You setup all field to same, because this system designed for MSA.
- But, SECRET_KEY MUST be different for each other
- Else other fields shared all project
- You NEVER, DO NOT share these secret.json file anywhere!


# TODO: Major Support Function
- [x] Search Music and User
- [x] Access Logging with DJango Login
- [x] Deploy to Kubernetes
- [x] External IP Logging
- [x] Bulk Uploader Script
- [x] Pending Delete
- [x] Stablize Continuous Deployment (Health Check)
- [x] Follow System
- [x] Streaming with YouTube
- [ ] SNS Feed Stream System
- [ ] Push Notification
- [ ] Subscription Billing System
- [ ] Auto Beat Matching
- [ ] Ment Layering while playing (Voice Composition)

# musicdaemon
Real broadcast daemon to stream icecast2.
It contains

- daemon body
- HTTP control server for daemon

And it's designed for run as a standalone mode.

# Radio Backend Environment Variable
See backend/Dockerfile or account/Dockerfile.

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
    
You must define these variables because secret information.

    ENV ENABLE_SWAGGER 1

    ENV DB_NAME 'apoweroftrance'
    ENV DB_HOST '127.0.0.1'
    ENV DB_USERNAME 'postgres'
    ENV DB_PASSWORD ''
    ENV DB_PORT 5432
    
    ENV REDIS_URL "127.0.0.1"
    ENV REDIS_PORT 6379
    ENV REDIS_DB 0
    
    ###########################
    # service depends control #
    
    # if 1, wait to start the depends service is up
    ENV WAIT_SERVICE 0
    ENV WAIT_URL "127.0.0.1"
    ENV WAIT_PORT 5432
    
    ###################
    # startup control #
    
    # pip install when start (dev usally)
    ENV INSTALL 0
    
    # pip makemigrations and migrate (dev usally)
    ENV MIGRATE 0
    
    # automatic start django
    ENV AUTOSTART 1


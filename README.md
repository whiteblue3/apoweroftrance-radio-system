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

# musicdaemon
Real broadcast daemon to stream icecast2.
It contains

- daemon body
- HTTP control server for daemon

And it's designed for run as a standalone mode.

# TODO
- [ ] Split Account and re-design to MSA
- [ ] Streaming with YouTube
- [ ] Auto Beat Matching
- [ ] Layer with Ment while playing (Voice Composition)

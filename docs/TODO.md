# TODO

#### [ Now ]
- [ ] Damage flag on board return.
- [ ] Split DB helpers into db.py once main.py gets unwieldy

#### [ Next ] 

#### [ Bugs ]

#### [ Security review (post-publish, ongoing) ]
- [ ] No CSRF protection on any POST route
- [ ] `remote_addr` is proxy-blind. The rate limiter breaks behind anything
- [ ] Rate limit dict is in-memory, per-process. It breaks with multiple workers
- [ ] `hmac.compare_digest` for username comparison
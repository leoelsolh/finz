# TODO

#### [ Now ]

#### [ Next ] 

#### [ Bugs ]

#### [ Security review (post-publish, ongoing) ]
- [ ] `remote_addr` is proxy-blind. The rate limiter breaks behind anything
- [ ] Rate limit dict is in-memory, per-process. It breaks with multiple workers
- [ ] `hmac.compare_digest` for username comparison
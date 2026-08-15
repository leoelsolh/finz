# TODO

#### [ Now ]
- [ ] SESSION_COOKIE_SECURE, flip after TLS
- [ ] Pick a hosting provider

#### [ Next ] 
- [ ] Multi-user accounts
- [ ] Stock management: add/remove boards, clear damage
- [ ] Wetsuits and body boards as separate hire items (£15/£10)
- [ ] LICENSE file

#### [ Bugs ]
- [ ] No migration system so schema changes mean deleting every .db file
- [ ] seed.py hardcodes "rental.db", uses naive datetime.now()
- [ ] No tests for availability arithmetic or the damage flow
- [ ] No way to clear damage when a board is repaired

#### [ Security review (post-publish, ongoing) ]
- [ ] `remote_addr` is proxy-blind. The rate limiter breaks behind anything
- [ ] Rate limit dict is in-memory, per-process. It breaks with multiple workers
- [ ] `hmac.compare_digest` for username comparison
# TODO

#### [ Now ]
- [ ] SESSION_COOKIE_SECURE, flip after TLS

#### [ Next ] 
- [ ] Multi-user accounts
- [ ] Stock management: add/remove boards
- [ ] Wetsuits and body boards as separate hire items (£15/£10)
- [ ] LICENSE file
- [ ] Add footer social links. Currently; href="#" (dead).
- [ ] Add HSTS and CSP headers before going live.

#### [ Bugs ]
- [ ] seed.py uses naive datetime.now() for booking dates
- [ ] No FK constraints, PRAGMA foreign_keys off: rentals.board_id references boards.id by convention only. No NOT NULL either.
- [ ] get_active_rentals duplicates the whole SELECT/JOIN across both if/else branches. Build the WHERE conditionally, keep one query.
- [ ] schema.init_db() runs as an import side effect (main.py, seed.py).
- [ ] test_db_connection is an empty pass that asserts nothing.
- [ ] Tests depend on ambient env (ADMIN_PASSWORD) and a shared on-disk test db.

#### [ Security review (post-publish, ongoing) ]
- [ ] `remote_addr` is proxy-blind. The rate limiter breaks behind anything
- [ ] Rate limit dict is in-memory, per-process. It breaks with multiple workers
- [ ] `hmac.compare_digest` for username comparison is cargo-cult (username is not a secret)
- [ ] .env stores ADMIN_PASSWORD in plaintext beside ADMIN_HASH (tests only). Seed a known hash in tests instead.

#### [ Nits ]
- [ ] mark_board_out returns rental_id; admin_out ignores it.
- [ ] .gitignore opens with `.*`, then also lists `.git*` and `.env` (already covered, and `.*` is broad).
# TODO
*Update once a month and check completed tasks*

#### [ Now ]
- [ ] SESSION_COOKIE_SECURE, flip after TLS

#### [ Next ]
- [ ] Multi-user accounts
- [ ] Change password function
- [x] Dashboard redesign: three pages (Counter / Stock / Analytics), bottom-pill + side-rail nav
- [x] Analytics: estimated income, bookings, busy-days chart, 1W/1M/1Y toggle
- [x] Wetsuits and body boards as separate hire items (£15/£10), via boards.category
- [x] Stock management: add / adjust quantity / archive (soft-delete) items
- [x] Quantity-aware send-out + grouped hires (hire_group), one name, one-button return with per-item damage
- [x] Mark a booking out (pre-fills send-out) + edit a booking
- [ ] LICENSE file
- [ ] Add footer social links. Currently; href="#" (dead).
- [ ] Add HSTS and CSP headers before going live.
- [ ] Review public pricing copy (index/book still say £25/£35)

#### [ Bugs ]
- [x] No migration system so schema changes mean deleting every .db file
- [x] negative-quantity Update returned 500 (string compared to int)
- [ ] seed.py uses naive datetime.now() for booking dates
- [ ] No FK constraints, PRAGMA foreign_keys off: rentals.board_id references boards.id by convention only. No NOT NULL either.
- [ ] get_active_rentals duplicates the whole SELECT/JOIN across both if/else branches. Build the WHERE conditionally, keep one query.
- [ ] run_migrations() runs as an import side effect (main.py, seed.py).
- [ ] test_db_connection is an empty pass that asserts nothing.
- [ ] Tests depend on ambient env (ADMIN_PASSWORD) and a shared on-disk test db.
- [ ] No regression tests for the new hire / booking / analytics features.

#### [ Security review (post-publish, ongoing) ]
- [ ] `remote_addr` is proxy-blind. The rate limiter breaks behind anything
- [ ] Rate limit dict is in-memory, per-process. It breaks with multiple workers
- [ ] `hmac.compare_digest` for username comparison is cargo-cult (username is not a secret)
- [ ] .env stores ADMIN_PASSWORD in plaintext beside ADMIN_HASH (tests only). Seed a known hash in tests instead.

#### [ Nits ]
- [x] mark_board_out returns rental_id; admin_out ignores it. (retired: admin_out uses mark_hire_out now)
- [ ] Old bookings columns size_requested / wetsuit are now unused, drop them in a later migration

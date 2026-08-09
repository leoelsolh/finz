# Finz Surf Hire
### [ Surf Rental App / made with flask ] 
[ Currently in Active Development ]

![CI](https://github.com/leoelsolh/fins-surf-rental/actions/workflows/ci.yml/badge.svg) ![Python](https://img.shields.io/badge/python-3.13-blue) ![Status](https://img.shields.io/badge/status-in%20development-orange)

 A booking and rental tracking site for a surfboard hire shop on the Gower peninsula in Wales.

My friend owns a surf shop which hires boards and wetsuits to visitors. She told me bookings currently come in by phone, to a personal mobile, and are noted on paper or not at all. Nobody had a reliable record of which boards were out and which came back. This site exists to fix both those problems. Now customers book online instead of calling, and whoever is running the shop can see at a glance what is out and with whom.

There are two halves. The public side lets customers see the boards, the prices, the opening hours and the address, and place a booking without phoning. The admin side, behind a login, lets the shop mark a board as gone out, mark it as returned, and see the day's bookings. The public side takes the weight off the phone. The admin side takes the weight off memory.

Built with Flask and sqlite3 on the Python standard library. No ORM, no framework beyond Flask itself. The frontend is plain CSS, mobile first, on the assumption that both customers and staff will mostly be on phones.

### [ How can I use this myself? ]
If you want to use this base project I've made to potentially help you run your own surf school or surf hire shop, here's what you need to consider.

_These need answering by the shop, not by the developer._

1. Whether a deposit is taken, and if so what is held and how it should be recorded.
2. How bookings should behave when nobody is at the shop. A manual open or closed switch is the likely answer, but the shop has not been asked yet.
3. Whether a second member of staff needs her own login, or whether a single shared admin account is enough.
4. Whether wetsuit stock needs tracking by size, or whether a wetsuit is simply bundled with a board.
5. Whether customer emails will ever be used for announcements. If they will, an explicit opt in at the point of booking is needed, unticked by default, along with a way to unsubscribe. This has to be designed in from the start rather than retrofitted.
6. Real prices, real stock, and the real shop phone number and address.

### [ Running it locally. ]
Once you've settled on the points above, here's how you can set this up on your local machine, using a devserver for pre-prod design and configuration.

###### [ Step One ] 
Install the requirements from the `requirements.txt` file:
```
git clone https://github.com/leoelsolh/finz.git
cd finz
pip install -r requirements.txt

```
###### [ Step Two ]
Create a .env file with the required variables. Things like admin_hash, admin_user, and secret_key have to be populated in order to create and maintain an authorized session. 
```
cat > .env <<'EOF'
ADMIN_HASH='<your_hashed_password>'
ADMIN_USER='<your_chosen_username>'
SECRET_KEY='<signing_key_for_sessions>'
EOF
```
The hash is generated in the shell with tools from `werkzeug.security` like this:
```
python3 
>>> from werkzeug.security import generate_password_hash
>>> print(generate_password_hash('your_password_here'))
 
```

###### [ Step Three ]
Lastly you're going to want to run the `run.sh` shell script, which will start a local flask server. *THIS IS NOT A PROD READY SERVER* so be careful.

### [ Running Tests. ]
The suite uses pytest, with ruff for linting. Both are in `requirements.txt`.

``` 
# run the test suite and ruff to lint
pytest test_app.py

# lint and test, the same gate CI runs 
./check.sh
```
Coverage includes public page loads, the admin authentication redirect, failed and successful login, rate limit lockout, and the database layer.

Tests run against a separate database defined in `conftest.py`, so they never read or write the development data in `rental.db`. `check.sh` runs ruff across the directory and then pytest, and is triggered by the GitHub Actions workflow on every push.

### [ Design decisions ]

**The rate limiter blocks correct credentials too.** After five failed attempts from an IP, every login attempt from that address returns 429 for an hour, including one with the right password. This is deliberate. If only wrong guesses were blocked, an attacker running a wordlist would be slowed down but never actually stopped, since the one attempt that matters would still succeed. The trade off is that a locked out member of staff has to wait, which is why a lockout notification is on the roadmap.

**The login route does the same work whether or not the username exists.** Both the username comparison and the password hash check run on every request, and the result is evaluated in a single combined branch. If the hash were skipped when the username was wrong, the difference in response time would tell an attacker which usernames are real.

**Configuration lives in one module.** `config.py` is the only place environment variables are read, and everything else imports from it. That single source of truth is what allows the test suite to point the whole application at a throwaway database, rather than tests writing into the same file the shop's data would live in.

# Hillend Surf Hire
## Surf Rental App / made with flask


A booking and rental tracking site for a surfboard hire shop at Hillend, Llangenith, on the Gower peninsula in Wales.

The shop hires boards and wetsuits to visitors. Bookings currently come in by phone, to a personal mobile, and are noted on paper or not at all. Nobody has a reliable record of which boards are out and which have come back. This site exists to fix both problems: customers book online instead of ringing, and the person running the shop can see at a glance what is out and with whom.

There are two halves. The public side lets customers see the boards, the prices, the opening hours and the address, and place a booking without phoning. The admin side, behind a login, lets the shop mark a board as gone out, mark it as returned, and see the day's bookings. The public side takes the weight off the phone. The admin side takes the weight off memory.

Opening hours are 9am to 6pm. Hire is flat rate per day. Prices are provisional: around £25 for a board, around £35 for a board and wetsuit together. Stock is roughly twenty boards. All figures in the current database are dummy data and must be confirmed with the shop before the site goes live.

Built with Flask and sqlite3 on the Python standard library. No ORM, no framework beyond Flask itself. The frontend is plain CSS, mobile first, on the assumption that both customers and staff will mostly be on phones.

#### V1.0

V1 is the smallest thing that solves the two stated problems. It is done when a customer can browse the boards and submit a booking that lands in the database, and the shop can log in, see the day's bookings, mark a board out, and mark it back in.

In scope: board list and single board pages served from the database; an hours, address and contact page; a booking form that captures name, phone, email, board and date, and writes it to the database; a confirmation shown to the customer; a single admin login; an admin view of board state, in or out; buttons to mark a board out and mark it returned; a view of the day's bookings.

Out of scope for V1, deliberately: wetsuits as separately tracked stock, an open or closed availability toggle, a second staff account, deposit records, email marketing, and any visual polish beyond a clean mobile layout.

Target: two weeks from 12 July 2026.

#### Open questions

These are unresolved and should not be guessed at. They need answering by the shop, not by the developer.

Whether a deposit is taken, and if so what is held and how it should be recorded.

How bookings should behave when nobody is at the shop. A manual open or closed switch is the likely answer, but the shop has not been asked yet.

Whether a second member of staff needs her own login, or whether a single shared admin account is enough.

Whether wetsuit stock needs tracking by size, or whether a wetsuit is simply bundled with a board.

Whether customer emails will ever be used for announcements. If they will, an explicit opt in at the point of booking is needed, unticked by default, along with a way to unsubscribe. This has to be designed in from the start rather than retrofitted.

Real prices, real stock, and the real shop phone number and address.
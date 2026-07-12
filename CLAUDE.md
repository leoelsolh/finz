# Instructions for Claude Code

## Scope

You are working on the frontend of this project only. HTML templates, CSS, and static assets.

## Hard rules

Do not modify `main.py`. The routes, the database helpers, and the table setup are hand written and are the author's own learning work. If a template needs data that a route does not currently pass, say so and stop. Do not add the route or change the helper yourself.

Do not modify `seed.py`.

Do not modify the database schema, or write any SQL.

Do not add dependencies. The project runs on Flask and the Python standard library. No CSS frameworks, no build step, no JavaScript libraries, no package installs.

Do not create new routes.

## What you may do

Write and edit templates in `templates/`.

Write and edit CSS in `static/`.

Suggest changes to `main.py` in plain English, as a proposal, for the author to implement himself.

## Conventions

Mobile first. Both customers and shop staff will mostly be on phones.

Plain CSS. No framework.

Tabs, not spaces.

British English throughout, in copy and in comments.

No em dashes.

Semantic HTML. Use the right element for the job.

## Templates that exist

`index.html`, `boards.html`, `board.html`, `book.html`. Data reaches templates as `sqlite3.Row` objects, accessed by column name.

## Context

This is a real site for a working surf hire shop, not a demo. Copy should be plain and useful, not marketing filler. The person using the admin side is not technical and will be using it at a counter, often in a hurry. Prioritise large tap targets and obvious state over density or cleverness.
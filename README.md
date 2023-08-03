# Pleroma purge old chats messages

A script to search for old chat messages on the Pleroma social network server and immediately delete them from the postgres database

```
pleroma_purge_old_chats -v

Connecting to the PostgreSQL database...

FOUND OLD CHAT MESSAGES: 3, with limit=3

DELETE OBJECT: '91'
DELETE FROM public.objects WHERE id = 91 AND data->>'type' = 'ChatMessage';
* DELETE REF OBJECT
DELETE FROM public.chat_message_references WHERE object_id = 91;

DELETE OBJECT: '4996'
DELETE FROM public.objects WHERE id = 4996 AND data->>'type' = 'ChatMessage';
* DELETE REF OBJECT
DELETE FROM public.chat_message_references WHERE object_id = 4996;

DELETE OBJECT: '4997'
DELETE FROM public.objects WHERE id = 4997 AND data->>'type' = 'ChatMessage';
* DELETE REF OBJECT
DELETE FROM public.chat_message_references WHERE object_id = 4997;

EMPTY CHATS FOUND: 3, with limit=3
** DELETE EMPTY CHAT: 1, created at: '2021-06-06 14:58:20'
DELETE FROM public.chats WHERE id = 00000279-e1d4-f46b-e87f-278b09920000;
** DELETE EMPTY CHAT: 2, created at: '2021-06-06 14:58:26'
DELETE FROM public.chats WHERE id = 00000279-e1d5-0c65-e87f-278b09920000;
** DELETE EMPTY CHAT: 3, created at: '2021-06-14 19:36:03'
DELETE FROM public.chats WHERE id = 0000027a-0c06-16be-1185-21bda6110000;
Database connection closed.
```

## BUILD

```
git clone https://github.com/lexxai/pleroma_purge_old_chats.git
cd pleroma_purge_old_chats

python -m venv .venv

# FreeBSD csh shell
source .venv/bin/activate.csh

# upgrade pip
python -m pip install --upgrade pip

```

# INSTALL

```
python -m pip install .

```

## RUN

```
pleroma_purge_old_chats -h
usage: purge_old_chats.py [-h] [-v [VERBOSE]] [-c CONFIG]

optional arguments:
  -h, --help            show this help message and exit
  -v [VERBOSE], --verbose [VERBOSE]
                        Detailed printing of the result of command execution.
  -c CONFIG, --config CONFIG
                        path to config ini file

pleroma_purge_old_chats -v
```

## CONFIG

[postgresql]
host=localhost
database=pleroma
user=pleroma

[limits]
hours=24
rows=500

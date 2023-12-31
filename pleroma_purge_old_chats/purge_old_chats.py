#!/usr/bin/env python

# https://www.postgresqltutorial.com/postgresql-python/connect/

import os
import sys
import argparse
import psycopg2
try:
    sys.path.append(os.path.dirname(__file__))
    from pleroma_purge_old_chats.config import config
except ImportError:
    from config import config


def vprint(*args):
    if verbose_mode:
        print(*args)


def purge_old_messages(config_file:str = None, demo:bool = None) -> None:
    """ Select old chats messages that oldest than 24h and purge it """
    conn = None

    LIMIT_ROWS = 100
    LIMIT_HOURS = 24

    try:
        # read connection parameters
        conf_data = config(config_file)
        db_params = conf_data['postgresql']
        limits = conf_data['limits']
        LIMIT_ROWS = int(limits.get('rows', LIMIT_ROWS))
        LIMIT_HOURS = int(limits.get('hours', LIMIT_HOURS))
    except (Exception) as error:
        print(error)

    SELECT_TIMEZONE = "SET TIMEZONE='UTC';"
    SELECT_CHAT_REF = "SELECT DISTINCT object_id FROM public.chat_message_references"\
                      " WHERE inserted_at <= NOW() - INTERVAL '{0:d} HOURS' LIMIT {1:d};".format(
                          LIMIT_HOURS, LIMIT_ROWS)

    # COUNT_CHAT_OBJECTS = "SELECT count(*) FROM public.chat_message_references"\
    #                      " WHERE chat_id = %s;"   

    SELECT_OBJECT = "SELECT * FROM public.objects"\
                    " WHERE id = %s AND data->>'type' = 'ChatMessage';"

    DELETE_OBJECT = "DELETE FROM public.objects WHERE id = %s AND data->>'type' = 'ChatMessage';"
    DELETE_CHAT_REF = "DELETE FROM public.chat_message_references WHERE object_id = %s;"
    DELETE_CHAT = "DELETE FROM public.chats WHERE id = %s;" 
    FIND_EMPTY_CHAT = "SELECT chats.id, chats.inserted_at  FROM chats"\
                      " LEFT JOIN chat_message_references ON chats.id = chat_message_references.chat_id"\
                      " WHERE chats.inserted_at <= NOW() - INTERVAL '{0:d} HOURS'"\
                      " AND chat_message_references.chat_id ISNULL"\
                      " ORDER BY chats.inserted_at LIMIT {1:d};".format(
                          LIMIT_HOURS, LIMIT_ROWS)

    delete_mode = demo is None
    #delete_mode = False

    try:
        # connect to the PostgreSQL server
        vprint('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**db_params)
        #transaction start
        with conn:
            with conn.cursor() as cur:
                # execute a statement
                # SELECT CHAT OBJECTS THAT OLDEST THAN 24h
                cur.execute( SELECT_TIMEZONE )
                cur.execute( SELECT_CHAT_REF )
                rows_found = cur.rowcount
                vprint(f"\nFOUND OLD CHAT MESSAGES: {rows_found}, with limit={LIMIT_ROWS}")
                rows = cur.fetchall()
                for row in rows:
                    object_id = row[0]
                    # SELECT/DELETE OBJECTS BY ID
                    vprint(f"\nDELETE OBJECT: '{object_id}'")
                    if delete_mode:
                        cur.execute( DELETE_OBJECT, (object_id,) )
                    else:
                        vprint(DELETE_OBJECT.replace('%s','{}').format(object_id))
                        cur.execute( SELECT_OBJECT, (object_id,) )
                    rows_deleted = cur.rowcount
                    if (rows_deleted):
                        vprint("* DELETE REF OBJECT")
                        if delete_mode:
                            cur.execute(DELETE_CHAT_REF, (object_id,))
                        else:
                            vprint(DELETE_CHAT_REF.replace('%s','{}').format(object_id))

                #now find empty chats references on chats, end purge it
                cur.execute( FIND_EMPTY_CHAT )
                rows_found = cur.rowcount
                if rows_found:
                    vprint(f"\nEMPTY CHATS FOUND: {rows_found}, with limit={LIMIT_ROWS}")
                    rows = cur.fetchall()
                    for i,row in  enumerate(rows):
                        chat_id = row[0]
                        inserted_at =  row[1]
                        vprint(f"** DELETE EMPTY CHAT: {i+1}, created at: '{inserted_at}'")
                        #DELETE CHAT
                        if delete_mode:
                            cur.execute(DELETE_CHAT, (chat_id,))
                        else:
                            vprint(DELETE_CHAT.replace('%s','{}').format(chat_id))

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            vprint('Database connection closed.')


def main():
    global verbose_mode
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', type=int, nargs='?', default=0, const=1,
                        help='Detailed printing of the result of command execution.')
    parser.add_argument('-c', '--config',
                        help='path to config ini file')
    parser.add_argument('--demo', nargs='?', const=True,
                        help='Demo mode without real delete records')
    args = parser.parse_args()
    verbose_mode = bool(int(args.verbose))
    #vprint(args)
    if args.config is not None:
        if not os.path.isfile(args.config):
            print(f"config file '{args.config}' not found")
            exit(1)
        else:
            args.config = os.path.abspath(args.config)


    purge_old_messages(args.config, demo=args.demo)

verbose_mode = False

if __name__ == '__main__':
    # pwd = os.path.dirname(__file__)
    # sys.path.append(pwd)
    # sys.path.append(os.path.join(pwd, 'data'))
    # print(sys.path)
    main()


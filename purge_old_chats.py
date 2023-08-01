#!/usr/bin/env python

# https://www.postgresqltutorial.com/postgresql-python/connect/

import psycopg2
from config import config

def purge_old_messages():
    """ Select old chats messages that oldest than 24h and purge it """
    conn = None

    LIMIT_ROWS = 100
    LIMIT_HOURS = 24

    try:
        # read connection parameters
        db_params = config()
        limits = config(section='limits')
        LIMIT_ROWS = int(limits.get('rows'))
        LIMIT_HOURS = int(limits.get('hours'))
    except (Exception) as error:
        print(error)


    SELECT_CHAT_REF = "SELECT DISTINCT object_id FROM public.chat_message_references"\
                      " WHERE inserted_at <= NOW() - INTERVAL '{0:d} HOURS' LIMIT {1:d};".format(
                          LIMIT_HOURS, LIMIT_ROWS)

    COUNT_CHAT_OBJECTS = "SELECT count(*) FROM public.chat_message_references"\
                         " WHERE chat_id = %s;"   

    SELECT_OBJECT = "SELECT * FROM public.objects"\
                    " WHERE id = %s AND data->>'type' = 'ChatMessage';"

    DELETE_OBJECT = "DELETE FROM public.objects WHERE id = %s AND data->>'type' = 'ChatMessage';"
    DELETE_CHAT_REF = "DELETE FROM public.chat_message_references WHERE object_id = %s;"
    DELETE_CHAT = "DELETE FROM public.chats WHERE id = %s;" 
    FIND_EMPTY_CHAT = "SELECT chats.id, chats.inserted_at  FROM chats"\
                      " LEFT JOIN chat_message_references ON chats.id = chat_message_references.chat_id"\
                      " WHERE chat_message_references.chat_id ISNULL"\
                      " ORDER BY chats.inserted_at LIMIT {};".format(LIMIT_ROWS)


    try:
        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**db_params)
        #transaction start
        with conn:
            with conn.cursor() as cur:
                # execute a statement
                # SELECT CHAT OBJECTS THAT OLDEST THAN 24h
                cur.execute( SELECT_CHAT_REF )
                rows_found = cur.rowcount
                print(f"\nFOUND OLD CHAT MESSAGES: {rows_found}, with limit={LIMIT_ROWS}")
                rows = cur.fetchall()
                for row in rows:
                    object_id = row[0]
                    # SELECT/DELETE OBJECTS BY ID
                    print(f"\nDELETE OBJECT: '{object_id}'")
                    #cur.execute( DELETE_OBJECT, (object_id,) )
                    print(DELETE_OBJECT.replace('%s','{}').format(object_id))
                    cur.execute( SELECT_OBJECT, (object_id,) )
                    rows_deleted = cur.rowcount
                    if (rows_deleted):
                        print("* DELETE REF OBJECT")
                        print(DELETE_CHAT_REF.replace('%s','{}').format(object_id))
                #now find empty chats references on chats, end purge it
                cur.execute( FIND_EMPTY_CHAT )
                rows_found = cur.rowcount
                if rows_found:
                    print(f"\nEMPTY CHATS FOUND: {rows_found}, with limit={LIMIT_ROWS}")
                    rows = cur.fetchall()
                    for i,row in  enumerate(rows):
                        chat_id = row[0]
                        inserted_at =  row[1]
                        print(f"** DELETE EMPTY CHAT: {i+1}, created at: '{inserted_at}'")
                        #DELETE CHAT
                        #cur.execute(DELETE_CHAT, chat_id)
                        print(DELETE_CHAT.replace('%s','{}').format(chat_id))

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')

if __name__ == '__main__':
    purge_old_messages()

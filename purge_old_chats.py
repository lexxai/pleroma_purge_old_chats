#!/usr/bin/env python

# https://www.postgresqltutorial.com/postgresql-python/connect/

import psycopg2
from config import config

def purge_old_messages():
    """ Select old chats messages that oldest than 24h and purge it """
    conn = None

    LIMIT_ROW = 10

    try:
        # read connection parameters
        db_params = config()
        limits = config(section='limits')
        LIMIT_ROW = limits.get('row')
    except (Exception) as error:
        print(error)



    SELECT_CHAT_REF = "SELECT DISTINCT object_id FROM public.chat_message_references"\
                      " WHERE inserted_at <= NOW() - INTERVAL '24 HOURS' LIMIT {};".format(LIMIT_ROW)

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
                      " ORDER BY chats.inserted_at LIMIT {};".format(LIMIT_ROW)


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
                print(f"\nFOUND OLD CHAT MESSAGES: {rows_found}, with limit={LIMIT_ROW}")
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
                        #o_row = cur.fetchone()
                        #print("MUST DELETED: ",rows_deleted, o_row )

                        #DELETE REF OBJECT
                        #cur.execute(DELETE_CHAT_REF, object_id)
                        print("* DELETE REF OBJECT")
                        print(DELETE_CHAT_REF.replace('%s','{}').format(object_id))

                        #COUNT CHAT_OBJECTS AFTER DELETING OLD
                        # cur.execute( COUNT_CHAT_OBJECTS, (chat_id,) )
                        # chat_objects_leaved = cur.fetchone()
                        # print(f"chat_objects_leaved for {chat_id}: {chat_objects_leaved[0]}")

                        # if chat_objects_leaved == 0:
                        #     print("** DELETE CHAT")
                        #     #cur.execute(DELETE_CHAT, chat_id)
                        #     print(DELETE_CHAT.replace('%s','{}').format(chat_id))
                cur.execute( FIND_EMPTY_CHAT )
                rows_found = cur.rowcount
                if rows_found:
                    print(f"\nEMPTY CHATS FOUND: {rows_found}, with limit={LIMIT_ROW}")
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

def connect():
    """ Connect to the PostgreSQL database server """
    conn = None
    try:
        # read connection parameters
        params = config()

        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)

        #transaction start
        with conn:
            with conn.cursor() as cur:
            # execute a statement
                print('PostgreSQL database version:')
                cur.execute('SELECT version()')
                # display the PostgreSQL database server version
                db_version = cur.fetchone()
                print(db_version)
            # close the communication with the PostgreSQL
                cur.close()

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')


if __name__ == '__main__':
    #connect()
    purge_old_messages()

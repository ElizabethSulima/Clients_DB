import psycopg2

def create_db(conn):
    with conn.cursor() as cur:
        cur.execute("""CREATE TABLE IF NOT EXISTS Client(client_id SERIAL PRIMARY KEY, firstname VARCHAR(80) NOT NULL,
                    lastname VARCHAR(100) NOT NULL, email VARCHAR(80) UNIQUE);""")
        conn.commit()
        cur.execute("""CREATE TABLE IF NOT EXISTS Phones(phone_id SERIAL PRIMARY KEY, 
                   client_id INTEGER NOT NULL REFERENCES Client(client_id),
                   phone CHAR(20) NOT NULL UNIQUE);""")
        conn.commit()

def add_client(conn, id, first_name, last_name, email, phone):
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO Client(client_id, firstname, lastname, email)
            VALUES (%s, %s, %s, %s) 
            RETURNING client_id, firstname, lastname, email;""",
            (id, first_name, last_name, email))
        conn.commit()
        cur.execute("""
            INSERT INTO Phones(client_id, phone)
            VALUES (%s, %s)
            RETURNING phone;""",
            (id, phone))
        conn.commit()
    print(cur.fetchone())
    result = cur.fetchone()
    return result

def add_phone(conn, client_id, phone):
    with conn.cursor() as cur:
        cur.execute(""" 
            INSERT INTO Phones(client_id, phone)
            VALUES (%s, %s)
            RETURNING phone_id, client_id, phone;""",
            (client_id, phone))
    conn.commit()
    print(cur.fetchall())
    result = cur.fetchall()
    return result

def change_client(conn, client_id, first_name, last_name, email, phone):
    with conn.cursor() as cur:
        cur.execute("""UPDATE Client
                       SET firstname=%s, lastname=%s, email=%s
                       WHERE client_id=%s""",
                    (first_name, last_name, email, client_id))
        conn.commit()
        cur.execute("""SELECT * FROM Client
                       WHERE client_id=%s""",
                    (client_id,))
        print(cur.fetchall())
        result = cur.fetchall()
        return result


def delete_phone(conn, client_id, phone):
    with conn.cursor() as cur:
        cur.execute("""DELETE FROM Phones 
                       WHERE client_id=%s AND phone=%s;""", (client_id, phone,))
        cur.execute("""SELECT * FROM Phones;""")
        print(cur.fetchall())
    result = cur.fetchall()
    return result


def delete_client(conn, client_id):
    with conn.cursor() as cur:
        cur.execute(""" DELETE FROM Client
                        WHERE client_id=%s;""",
                       (client_id,))
        conn.commit()
    print(cur.fetchall())
    result = cur.fetchall()
    return result

def find_client(conn, first_name='%s', last_name='%s', email='%s', phone='%s'):
    with conn.cursor() as cur:
        cur.execute("""SELECT client_id FROM Client
                       WHERE firstname LIKE %s 
                       OR lastname LIKE %s
                       OR email LIKE %s 
                       OR (SELECT client_id FROM Phones WHERE phone LIKE %s AS phone_);""",
                    (first_name, last_name, email, phone))
        conn.commit()
    print(cur.fetchall())
    result = cur.fetchall()
    return result

if __name__ == '__main__':
    with psycopg2.connect(database="client_db", user="postgres", password="123", host="localhost") as conn:
        create_db(conn)
        add_client(conn, 1,  'Mark', 'Kors', 'kkors@mail.ru', 112544368)
        add_client(conn, 2, 'Alice', 'Wind', 'w.al@mail.ru', 7414775421)
        add_phone(conn, 2, 18567429474)
        change_client(conn, 2, 'Jack', 'London', 'j_lon@yandex.ru', 7894524334)
        delete_phone(conn, 1, 112544368)
        delete_client(conn, 2,)
        find_client(conn, 1,  'Mark', 'Kors', 'kkors@mail.ru')
        conn.commit()
        with conn.cursor() as cur:
            cur.execute("""
                SELECT * FROM Client;
                """)
            print('fetchall:', cur.fetchall())
            cur.execute("""
                            SELECT * FROM Phones;
                            """)
            print('fetchall:', cur.fetchall())
            cur.execute("""DROP TABLE Phones;
                           DROP TABLE Client;""")
        conn.commit()
    conn.close()

import sqlite3


conn = sqlite3.connect('search_results.db', check_same_thread=False)
cur = conn.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS search( 
   id INT,
   id_user INT);
""")
conn.commit()


def all_users():
    cur.execute('SELECT * FROM search')
    result = cur.fetchall()
    return result


def add_user(params, user):
    search_id = params['id']
    cur.execute(f'INSERT INTO search(id, id_user) VALUES(?, ?)', (search_id, user))
    conn.commit()


def check_user(user_search, user_id):
    all_info = all_users()
    for user in all_info:
        if int(user_search) == int(user[0]) and int(user_id) == int(user[1]):
            return True

import sqlite3


conn = sqlite3.connect('search_results.db', check_same_thread=False)
cur = conn.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS search( 
   id INT,
   name TEXT,
   link TEXT);
""")
conn.commit()


def all_users():
    cur.execute('SELECT * FROM search')
    result = cur.fetchall()
    return result


def add_user(params):
    id = params['id']
    name = params['name']
    link = f'vk.com/id{params["id"]}'
    cur.execute(f'INSERT INTO search(id, name, link) VALUES(?, ?, ?)', (id, name, link))
    conn.commit()


def check_user(user_id):
    all_info = all_users()
    for user in all_info:
        if int(user_id) == int(user[0]):
            return True

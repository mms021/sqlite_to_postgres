import sqlite3
import psycopg2
from db_models import Genre, GenreFW, Person, PersonFW, FilmW

N = 30

TRUNCATE_TEBLES = False

SQLLITE = 'db.sqlite'

PG_CONECT = {
    'dbname': 'movies_database',
    'user': 'app',
    'password': '123qwe',
    'host': '127.0.0.1',
    'port': 5433,
    'options': '-c search_path=content',
}


try:
    connect = sqlite3.connect(SQLLITE)
    cursor = connect.cursor()

    sq = cursor.execute("SELECT * FROM genre;")
    genre = [Genre(i[0], i[1], i[2]) for i in sq.fetchall()]

    sq = cursor.execute("SELECT * FROM genre_film_work;")
    genre_fw = [GenreFW(i[0], i[1], i[2], i[3]) for i in sq.fetchall()]

    sq = cursor.execute("SELECT * FROM person_film_work;")
    person_fw = [PersonFW(i[0], i[1], i[2], i[3], i[4]) for i in sq.fetchall()]

    sq = cursor.execute("SELECT * FROM person;")
    person = [Person(i[0], i[1], i[2]) for i in sq.fetchall()]

    sq = cursor.execute("""
    SELECT id, title, description,
    rating, type, creation_date  FROM film_work;""").fetchall()
    film_w = [FilmW(i[0], i[1], i[2], i[3], i[4], i[5]) for i in sq]

    cursor.close()
except sqlite3.Error as error:
    print("Ошибка при подключении к sqlite", error)
finally:
    if (connect):
        connect.close()


with psycopg2.connect(**PG_CONECT) as conn, conn.cursor() as cursor:

    if TRUNCATE_TEBLES:
        cursor.execute("""TRUNCATE content.genre""")
        cursor.execute("""TRUNCATE content.genre_film_work""")
        cursor.execute("""TRUNCATE content.person_film_work""")
        cursor.execute("""TRUNCATE content.person""")
        cursor.execute("""TRUNCATE content.film_work""")

   
    for i in range(N, len(genre), N):
        args = ','.join(item.tupl_str() for item in genre[i: i+N])
        cursor.execute(f"""
        INSERT INTO content.genre (id, name, description)
        VALUES {args}
        ON CONFLICT (id) DO UPDATE SET
        name=EXCLUDED.name,
        description=EXCLUDED.description
        """)

    for i in range(N, len(genre_fw), N):
        args = ','.join(item.tupl_str() for item in genre_fw[i: i+N])
        cursor.execute(f"""
        INSERT INTO content.genre_film_work (id, film_work_id,
                                            genre_id, created)
        VALUES {args}
        ON CONFLICT (id) DO UPDATE SET
        film_work_id=EXCLUDED.film_work_id,
        genre_id=EXCLUDED.genre_id,
        created=EXCLUDED.created
        """)

    for i in range(N, len(person_fw), N):
        args = ','.join(item.tupl_str() for item in person_fw[i: i+N])
        cursor.execute(f"""
        INSERT INTO content.person_film_work (id, film_work_id,
                                            person_id, role, created)
        VALUES {args}
        ON CONFLICT (id) DO UPDATE SET
        film_work_id=EXCLUDED.film_work_id,
        person_id=EXCLUDED.person_id,
        role=EXCLUDED.role,
        created=EXCLUDED.created
        """)

    for i in range(N, len(person), N):
        args = ','.join(item.tupl_str() for item in person[i: i+N])
        cursor.execute(f"""
        INSERT INTO content.person (id, full_name, gender)
        VALUES {args}
        ON CONFLICT (id) DO UPDATE SET
        full_name=EXCLUDED.full_name,
        gender=EXCLUDED.gender
        """)


    for i in range(N, len(film_w), N):
        args = ','.join(cursor.mogrify("(%s, %s ,%s ,%s, %s)", item.tupl()).decode() for item in film_w[i: i+N])
        cursor.execute(f"""
        INSERT INTO content.film_work (id, title, description,type, rating)
        VALUES {args}
        ON CONFLICT (id) DO UPDATE SET
        title=EXCLUDED.title,
        description=EXCLUDED.description,
        rating=EXCLUDED.rating,
        type=EXCLUDED.type,
        creation_date=EXCLUDED.creation_date,
        """)


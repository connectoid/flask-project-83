import psycopg2
from psycopg2.extras import DictCursor

from dataclasses import dataclass, field
from datetime import datetime, timezone, date


@dataclass
class URLCheck:
    url_id: int
    status_code: int
    h1: str
    title: str
    description: str
    created_at: datetime
    id: int | None = None

    def __post_init__(self):
        self.created_at = self.created_at.date()
        self.status_code = self.status_code if self.status_code else ''


@dataclass
class URL:
    name: str
    created_at: datetime
    id: int | None = None

    def __post_init__(self):
        self.created_at = self.created_at.date()


class URLRepository:
    def __init__(self, conn):
        self.conn = conn

    def get_content(self):
        with self.conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute("SELECT * FROM urls")
            rows = cur.fetchall()
            # return [URL(**row) for row in rows]
            urls = [dict(row) for row in rows]
            for url in urls:
                url['created_at'] = url['created_at'].date()
            return urls


    def find(self, id):
        with self.conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute("SELECT * FROM urls WHERE id = %s", (id,))
            row = cur.fetchone()
            return dict(row) if row else None


    def get_by_term(self, search_term=""):
        with self.conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute(
                """
                    SELECT * FROM urls
                    WHERE name ILIKE %s
                """,
                (f"%{search_term}%", f"%{search_term}%"),
            )
            rows = cur.fetchall()
            return [URLCheck(**row) for row in rows]
    

    def get_url_by_name(self, name):
        with self.conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute('SELECT * FROM urls WHERE name = %s', (name,))
            return cur.fetchone()


    def save(self, url):
        if "id" in url and url["id"]:
            self._update(url)
            
        else:
            self._create(url)
        return url["id"]


    def get_checks(self, url_id):
        with self.conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute(
                """
                    SELECT * FROM url_checks
                    WHERE url_id = %s
                """,
                (url_id,)
            )
            rows = cur.fetchall()
            return [URLCheck(**row) for row in rows]


    def get_last_check(self, url_id):
        with self.conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute("SELECT * FROM url_checks WHERE url_id = %s", (url_id,))
            rows = cur.fetchall()
            last_check = URLCheck(**rows[-1]) if rows else None
            return last_check if last_check else None



    def check(self, url_id, created_at, h1, title, description, status_code):
        print(url_id)
        print(created_at)
        print(h1)
        print(title)
        print(description)
        print(status_code)
        with self.conn.cursor() as cur:
            cur.execute(
                "INSERT INTO url_checks (url_id, status_code, h1, title, description, created_at) VALUES (%s, %s, %s, %s, %s, %s) " \
                "RETURNING id",
                (url_id, status_code, h1, title, description, created_at),
            )
            id = cur.fetchone()[0]
        self.conn.commit()
        return id


    def _update(self, url):
        with self.conn.cursor() as cur:
            cur.execute(
                "UPDATE urls SET name = %s",
                (url["name"], url["created_at"], url["id"]),
            )
        self.conn.commit()

    def _create(self, url):
        with self.conn.cursor() as cur:
            cur.execute(
                "INSERT INTO urls (name, created_at) VALUES (%s, %s) RETURNING id",
                (url["name"], url["created_at"]),
            )
            row = cur.fetchone()
            id = row[0]
            url["id"] = id
        self.conn.commit()



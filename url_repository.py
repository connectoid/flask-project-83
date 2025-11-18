import psycopg2
from psycopg2.extras import DictCursor

from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class URLCheck:
    url_id: int
    status_code: int
    h1: str
    title: str
    description: str
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc))
    id: int | None = None


@dataclass
class URL:
    name: str
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc))
    id: int | None = None


class URLRepository:
    def __init__(self, conn):
        self.conn = conn

    def get_content(self):
        with self.conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute("SELECT * FROM urls")
            return [dict(row) for row in cur]

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
            return cur.fetchall()
    

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


    def check(self, url_id, created_at):
        with self.conn.cursor() as cur:
            cur.execute(
                "INSERT INTO url_checks (url_id, created_at) VALUES (%s, %s) RETURNING id",
                (url_id, created_at),
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
            print(row)
            id = row[0]
            url["id"] = id
        self.conn.commit()



from pathlib import Path
from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parent / ".env", override=True)
import os
import click
import psycopg2
import psycopg2.extras
from flask import current_app, g


def get_db():
    """Open one database connection per request."""
    if "db" not in g:
        g.db = psycopg2.connect(
            os.environ["DATABASE_URL"],
            cursor_factory=psycopg2.extras.RealDictCursor,  # rows behave like dictionaries
        )
    return g.db


def close_db(e=None):
    """Close the connection when the request ends."""
    conn = g.pop("db", None)
    if conn is not None:
        conn.close()


def query(sql, params=None, one=False):
    """Run a SELECT and return rows (or a single row if one=True)."""
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute(sql, params)
        return cur.fetchone() if one else cur.fetchall()


def execute(sql, params=None):
    """Run INSERT / UPDATE / DELETE and commit."""
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute(sql, params)
    conn.commit()


def init_db():
    """Run schema.sql to create tables and seed data."""
    conn = get_db()
    with current_app.open_resource("schema.sql") as f:
        sql = f.read().decode("utf8")
    with conn.cursor() as cur:
        cur.execute(sql)
    conn.commit()


@click.command("init-db")
def init_db_command():
    """Terminal command: flask --app app init-db"""
    init_db()
    click.echo("Supabase database created and seeded.")


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
import json
import os
import re
from collections import Counter
from functools import wraps

import click
from dotenv import load_dotenv
from flask import (Flask, render_template, request, redirect, url_for,
                   session, flash, jsonify, abort)
from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv(override=True)

import calc
import db

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-change-me")
db.init_app(app)

# Default catalog data (inserted once by: flask --app app seed)
APPLIANCES = [
    ("light", "Lights", "💡", 10, 10, 6),
    ("fan", "Fans", "🌀", 75, 5, 8),
    ("ac", "Air conditioners", "❄️", 1500, 2, 6),
    ("fridge", "Refrigerators", "🧊", 150, 2, 10),
    ("tv", "TVs", "📺", 100, 3, 5),
    ("heater", "Water heaters", "🚿", 2000, 2, 2),
    ("other", "Other appliances", "🔌", 100, 5, 4),
]
PANELS = [("Mono PERC 540W", 540, 2.6, 15500), ("Mono TOPCon 590W", 590, 2.7, 17500)]
BATTERIES = [("LiFePO4 5 kWh", 5, 85000, "LiFePO4"), ("LiFePO4 10 kWh", 10, 160000, "LiFePO4")]


# ---------------------------------------------------------------
# CLI: seed default data
# ---------------------------------------------------------------
@app.cli.command("seed")
def seed():
    """Insert default appliances, panels, batteries, settings and the admin user."""
    conn = db.get_db()
    with conn.cursor() as cur:
        cur.execute("SELECT 1 FROM appliances LIMIT 1")
        if cur.fetchone():
            click.echo("Already seeded. Nothing to do.")
            return
        cur.executemany(
            "INSERT INTO appliances (key, name, icon, watts, qty, hours) VALUES (%s,%s,%s,%s,%s,%s)",
            APPLIANCES)
        cur.executemany(
            "INSERT INTO solar_panels (model, watts, area_m2, price) VALUES (%s,%s,%s,%s)", PANELS)
        cur.executemany(
            "INSERT INTO batteries (model, kwh, price, chemistry) VALUES (%s,%s,%s,%s)", BATTERIES)
        cur.executemany(
            "INSERT INTO settings (key, value) VALUES (%s,%s)", list(calc.DEFAULT_SETTINGS.items()))
        admin_pw = os.environ.get("ADMIN_PASSWORD", "admin123")
        cur.execute(
            "INSERT INTO users (name, email, password_hash, is_admin) VALUES (%s,%s,%s,TRUE)",
            ("Admin", "admin@solar.local", generate_password_hash(admin_pw)))
    conn.commit()
    click.echo("Seeded. Admin login: admin@solar.local")


# ---------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------
def settings():
    rows = db.query("SELECT key, value FROM settings ORDER BY key")
    return {r["key"]: r["value"] for r in rows}


def login_required(f):
    @wraps(f)
    def w(*a, **k):
        if "uid" not in session:
            flash("Please log in to continue.", "error")
            return redirect(url_for("login"))
        return f(*a, **k)
    return w


def admin_required(f):
    @wraps(f)
    @login_required
    def w(*a, **k):
        if not session.get("admin"):
            abort(403)
        return f(*a, **k)
    return w


def own_project(pid):
    p = db.query("SELECT * FROM projects WHERE id = %s AND user_id = %s",
                 (pid, session["uid"]), one=True)
    if not p:
        abort(404)
    return p


def save_project(inp, pid=None):
    errs = calc.validate(inp)
    if not (inp.get("name") or "").strip():
        errs.append("Please give your project a name.")
    if errs:
        return None, errs

    res = calc.compute(inp, settings())
    vals = (inp["name"].strip()[:80], inp.get("property_type", "Homestay"),
            inp["state"], inp["city"], res["solar_kw"], res["battery_kwh"],
            res["cost"], json.dumps(inp), json.dumps(res))

    conn = db.get_db()
    with conn.cursor() as cur:
        if pid:
            cur.execute(
                "UPDATE projects SET name=%s, property_type=%s, state=%s, city=%s, "
                "solar_kw=%s, battery_kwh=%s, cost=%s, inputs=%s, results=%s "
                "WHERE id=%s AND user_id=%s",
                vals + (pid, session["uid"]))
        else:
            cur.execute(
                "INSERT INTO projects (name, property_type, state, city, solar_kw, "
                "battery_kwh, cost, inputs, results, user_id) "
                "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id",
                vals + (session["uid"],))
            pid = cur.fetchone()["id"]
    conn.commit()
    return pid, []


# ---------------------------------------------------------------
# Public + auth
# ---------------------------------------------------------------
@app.route("/")
def home():
    return render_template("home.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        n, e, p, c = (request.form.get(k, "").strip() for k in ("name", "email", "password", "confirm"))
        e = e.lower()
        err = None
        if not n:
            err = "Please enter your name."
        elif not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", e):
            err = "Please enter a valid email address."
        elif len(p) < 8 or not re.search(r"\d", p) or not re.search(r"[A-Za-z]", p):
            err = "Password needs 8+ characters with letters and numbers."
        elif p != c:
            err = "Passwords do not match."
        elif db.query("SELECT 1 FROM users WHERE email = %s", (e,), one=True):
            err = "An account with this email already exists."

        if err:
            flash(err, "error")
        else:
            conn = db.get_db()
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO users (name, email, password_hash) VALUES (%s,%s,%s) RETURNING id",
                    (n, e, generate_password_hash(p)))
                uid = cur.fetchone()["id"]
            conn.commit()
            session.update(uid=uid, name=n, admin=False)
            return redirect(url_for("start"))
    return render_template("auth.html", mode="signup")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        u = db.query("SELECT * FROM users WHERE email = %s",
                     (request.form.get("email", "").strip().lower(),), one=True)
        if u and check_password_hash(u["password_hash"], request.form.get("password", "")):
            session.clear()
            session.update(uid=u["id"], name=u["name"], admin=bool(u["is_admin"]))
            return redirect(url_for("start"))
        flash("Incorrect email or password.", "error")
    return render_template("auth.html", mode="login")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


@app.route("/start")
@login_required
def start():
    return render_template("start.html")


# ---------------------------------------------------------------
# Wizard + projects
# ---------------------------------------------------------------
def wizard_page(init=None, edit_id=None):
    apps = [dict(r) for r in db.query(
        "SELECT key, name, icon, watts, qty, hours FROM appliances ORDER BY id")]
    states = {k: v[1] for k, v in calc.STATES.items()}
    return render_template("wizard.html", init=init, edit_id=edit_id, apps=apps, states=states)


@app.route("/wizard")
@login_required
def wizard():
    return wizard_page()


@app.route("/projects/<int:pid>/edit")
@login_required
def edit_project(pid):
    p = own_project(pid)
    return wizard_page(json.loads(p["inputs"]), pid)


@app.route("/api/projects", methods=["POST"])
@login_required
def api_create():
    pid, errs = save_project(request.get_json(force=True, silent=True) or {})
    return (jsonify(errors=errs), 400) if errs else jsonify(url=url_for("project", pid=pid))


@app.route("/api/projects/<int:pid>", methods=["PUT"])
@login_required
def api_update(pid):
    own_project(pid)
    _, errs = save_project(request.get_json(force=True, silent=True) or {}, pid)
    return (jsonify(errors=errs), 400) if errs else jsonify(url=url_for("project", pid=pid))


@app.route("/projects")
@login_required
def projects():
    rows = db.query("SELECT * FROM projects WHERE user_id = %s ORDER BY id DESC", (session["uid"],))
    return render_template("projects.html", projects=rows)


@app.route("/projects/<int:pid>")
@login_required
def project(pid):
    p = own_project(pid)
    return render_template("project.html", p=p, inp=json.loads(p["inputs"]), r=json.loads(p["results"]))


@app.route("/projects/<int:pid>/report")
@login_required
def report(pid):
    p = own_project(pid)
    return render_template("report.html", p=p, inp=json.loads(p["inputs"]), r=json.loads(p["results"]))


@app.route("/projects/<int:pid>/recalc", methods=["POST"])
@login_required
def recalc(pid):
    p = own_project(pid)
    _, errs = save_project(json.loads(p["inputs"]) | {"name": p["name"]}, pid)
    flash(errs[0] if errs else "Recalculated with the latest assumptions.", "error" if errs else "ok")
    return redirect(url_for("project", pid=pid))


@app.route("/projects/<int:pid>/delete", methods=["POST"])
@login_required
def delete_project(pid):
    own_project(pid)
    db.execute("DELETE FROM projects WHERE id = %s", (pid,))
    flash("Project deleted.", "ok")
    return redirect(url_for("projects"))


# ---------------------------------------------------------------
# Admin
# ---------------------------------------------------------------
@app.route("/admin")
@admin_required
def admin():
    rows = db.query(
        "SELECT p.*, u.email FROM projects p JOIN users u ON u.id = p.user_id ORDER BY p.id DESC")
    types = Counter(r["property_type"] for r in rows)
    stats = {
        "users": db.query("SELECT COUNT(*) AS c FROM users", one=True)["c"],
        "projects": len(rows),
        "avg_kw": round(sum(r["solar_kw"] for r in rows) / len(rows), 1) if rows else 0,
        "top_type": types.most_common(1)[0][0] if types else "-",
    }
    return render_template(
        "admin.html",
        stats=stats,
        projects=rows,
        users=db.query("SELECT id, name, email, is_admin, created_at FROM users ORDER BY id"),
        appliances=db.query("SELECT * FROM appliances ORDER BY id"),
        panels=db.query("SELECT * FROM solar_panels ORDER BY id"),
        batteries=db.query("SELECT * FROM batteries ORDER BY id"),
        settings=settings(),
    )


@app.route("/admin/settings", methods=["POST"])
@admin_required
def admin_settings():
    new_values = {}
    for k in calc.DEFAULT_SETTINGS:
        try:
            v = float(request.form[k])
            if v <= 0:
                raise ValueError
            new_values[k] = v
        except (KeyError, ValueError):
            flash(f"Invalid value for {k}.", "error")
            return redirect(url_for("admin"))

    conn = db.get_db()
    with conn.cursor() as cur:
        for k, v in new_values.items():
            cur.execute("UPDATE settings SET value = %s WHERE key = %s", (v, k))
    conn.commit()
    flash("Parameters updated. Use Recalculate on a project to apply them.", "ok")
    return redirect(url_for("admin"))


@app.route("/admin/projects/<int:pid>/delete", methods=["POST"])
@admin_required
def admin_delete_project(pid):
    db.execute("DELETE FROM projects WHERE id = %s", (pid,))
    return redirect(url_for("admin"))


if __name__ == "__main__":
    app.run(debug=True)
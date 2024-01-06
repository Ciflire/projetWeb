from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    redirect,
    url_for,
    Response,
)
from flask import g
import sqlite3
from datetime import datetime
import json
import sys


app = Flask(__name__, static_folder="static")

DATABASE = "data/database.sqlite3"  # le nom du fichier de votre base sqlite3


def get_db():  # cette fonction permet de créer une connexion à la base
    # ou de récupérer la connexion existante
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


@app.teardown_appcontext
def close_connection(exception):  # pour fermer la connexion proprement
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()


@app.route("/createchallenge")
def createchallenge():
    return render_template("createchallenge.html")


@app.route("/classements")
def classements():
    return render_template("tous_les_classements.html")



@app.route("/api/challenge/create/<name>/<end_date>")
def creationchallenge(name,end_date):
    creation_date=datetime.now().timestamp()
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO challenges (name, creation_date, end_date)
        VALUES (?,?,?)
    """,
    (name, creation_date, end_date),
    )

    conn.commit()
    conn.close()

    message = "Les données ont été enregistrées avec succès!"

    return (message)

@app.route("/api/challenge/change/<id_challenge>/<name>/<end_date>")
def updatechallenge(id_challenge,name,end_date):
    creation_date=datetime.now().timestamp()
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE challenges
        SET name = (?),end_date = (?)
        WHERE id_challenge = (?);

    """,
    (name, end_date, id_challenge),
    )

    conn.commit()
    conn.close()

    message = "Les changements ont été enregistrés avec succès!"

    return (message)

@app.route("/api/challenge/delete/<id_challenge>")
def deletechallenge(id_challenge):
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    cur.execute(
        """
        DELETE FROM validations
        WHERE id_challenge = (?);
        """,
         (id_challenge),
    )
    cur.execute(
        """
        DELETE FROM challenges
        WHERE id_challenge = (?);
        """,
    (id_challenge),
    )

    conn.commit()
    conn.close()

    message = "Les changements ont été enregistrés avec succès!"

    return (message)


@app.route("/api/users/create/<name>/<admin>/<password>/<hash>")
def creationuser(name,admin, password, hash):
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO users (name, admin, password, hash)
        VALUES (?,?,?,?)
    """,
    (name,admin, password, hash),
    )

    conn.commit()
    conn.close()

    message = "Les données ont été enregistrées avec succès!"

    return (message)


@app.route("/api/users/<id_user>")
def user_json(id_user):
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    cur.execute(
        f"""SELECT * FROM users where id_challenge = {id_user};"""
    )
    info = cur.fetchall()
    conn.close()
    # print(info, file=sys.stderr)
    return jsonify(info)

@app.route("/api/users/all")
def all_users():
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    cur.execute(
        f"""SELECT id_user,name FROM users;"""
    )
    info = cur.fetchall()
    conn.close()
    # print(info, file=sys.stderr)
    return jsonify(info)


@app.route("/api/challenge/<id_challenge>")
def challenge_json(id_challenge):
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    cur.execute(
        f"""SELECT * FROM challenges where id_challenge = {id_challenge};"""
    )
    info = cur.fetchall()
    conn.close()
    # print(info, file=sys.stderr)
    return jsonify(info)


@app.route("/api/validations/<id_user>/<id_challenge>")
def validations_json(id_user, id_challenge):
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    cur.execute(
        f"""SELECT * FROM validations where (id_user = {id_user}) and (id_challenge = {id_challenge});""",
    )
    info = cur.fetchall()
    conn.close()
    # print(info, file=sys.stderr)
    return jsonify(info)


if __name__ == "__main__":
    app.run(debug=True)

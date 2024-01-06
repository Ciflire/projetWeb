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


@app.route("/generate_json_challenge", methods=["POST"])
def generate_jsonz():
    user_data = {
        "name": request.form["name"],
        "creation_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "end_date": request.form["end_date"],
    }

    # Stocker les données dans la base de données
    conn = sqlite3.connect(
        "data/database.sqlite3"
    )  # Remplacez 'site.db' par le nom de votre base de données
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO challenges (name, creation_date, end_date)
        VALUES (?, ?, ?)
    """,
        (user_data["name"], user_data["creation_date"], user_data["end_date"]),
    )

    conn.commit()
    conn.close()

    # return jsonify ({'message': 'Données enregistrées avec succès'})

    message = "Les données ont été enregistrées avec succès!"

    return render_template("popup.html", message=message)


@app.route("/api/users/<id_user>")
def user_json(id_user):
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    cur.execute(
        f"""SELECT * FROM challenges where id_challenge = {id_user};"""
    )
    info = cur.fetchall()
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
    # print(info, file=sys.stderr)
    return jsonify(info)


if __name__ == "__main__":
    app.run(debug=True)

import secrets
import sqlite3
import sys  # noqa: F401
from datetime import datetime

import requests
from flask import (
    Flask,
    Response,
    flash,
    g,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    logout_user,
    current_user,
    login_required,
)
from werkzeug.security import check_password_hash, generate_password_hash


app = Flask(__name__, static_folder="static")
app.config["SECRET_KEY"] = "1234567890"
app.config["DATABASE"] = "static/database.db"
login_manager = LoginManager()
login_manager.init_app(app)


# DB related
def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource("schema.sql", mode="r") as f:
            db.cursor().executescript(f.read())
        db.commit()


def get_db():
    db = sqlite3.connect(app.config["DATABASE"])
    db.row_factory = sqlite3.Row
    return db


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, "sqlite_db"):
        g.sqlite_db.close()


class User(UserMixin):
    def __init__(self, username, password):
        self.id = user_id
        self.username = username
        self.password = password


@login_manager.user_loader
def load_user(user_id):
    db = get_db()
    user_data = db.execute(
        "SELECT * FROM user WHERE id = ?", (user_id,)
    ).fetchone()
    if user_data:
        return User(user_data["id"], user_data["username"])
    return None


user = User("admin", "password")

login_manager.user_loader(load_user)


def connect_db():
    return sqlite3.connect(app.config["DATABASE"])


def generateToken() -> str:
    token = secrets.token_hex(16)
    return token


@app.before_request
def before_request():
    g.db = connect_db()


@app.teardown_request
def teardown_request(exception):
    if hasattr(g, "db"):
        g.db.close()


# accueil
@app.route("/")
def home():
    return render_template("accueil.html")


# all users
@app.route("/users")
def users():
    return render_template("allusers.html")


# challenge
@app.route("/challenge")
def challenge():
    return render_template("challenge.html")


# profile
@app.route("/profile/<id>")
def profile(id):
    return render_template("profile.html")


# user modif profile
@app.route("/profile/modify/<id>")
def modifyProfile(id):
    return render_template("usermodifprofile.html")


# all challenge
@app.route("/challenges")
def challenges():
    return render_template("allchallenge")


# all challenge admin
@app.route("/challenge")
def deleteChallenge():
    return render_template("allchallengeadmin.html")


# all challenge admin remove

# admin Create challenge
# admin modify challenge
# challenge admin
# challenge admin add user
# challenge registre


@app.route("/template")
def template():
    return render_template("template.html")


login_manager.user_loader(load_user)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect("/profile")

    if request.method == "POST":
        # Get the username and password from the request
        username = request.form["username"]
        password = request.form["password"]

        # Check if the username and password are valid
        if user.username == username and user.password == password:
            # Login the user
            login_user(user)
            return redirect("")

        # Otherwise, show an error message
        return render_template(
            "login.html", error="Invalid username or password."
        )

    # Render the login form for GET requests
    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # Utilisez SHA-256 pour hacher le mot de passe
        hashed_password = generate_password_hash(password)

        cursor = g.db.cursor()
        cursor.execute(
            "INSERT INTO users (name, admin, password, hash) VALUES (?, 1, ?, ?)",
            (username, hashed_password, hashed_password),
        )
        g.db.commit()

        flash("Your account has been created!", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        cursor = g.db.cursor()
        cursor.execute("SELECT * FROM users WHERE name = ?", (username,))
        user = cursor.fetchall()
        if user and (check_password_hash(user[0][3], password)):
            session["user_id"] = user[0]
            return render_template("popup.html", message="Connexion reussie")
        else:
            render_template(
                "popup.html",
                message="""
                Login unsuccessful. Please check your username and password.""",
            )

    return render_template("connexion.html")


@app.route("/createchallenge")
def createchallenge():
    return render_template("createchallenge.html")


@app.route("/classements")
def classements():
    return render_template("tous_les_classements.html")


@app.route("/api/challenge/create/<name>/<end_date>")
def creationchallenge(name, end_date):
    creation_date = datetime.now().timestamp()
    conn = sqlite3.connect(app.config["DATABASE"])
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

    return message


@app.route("/api/challenge/change/<id_challenge>/<name>/<end_date>")
def updatechallenge(id_challenge, name, end_date):
    creation_date = datetime.now().timestamp()
    conn = sqlite3.connect(app.config["DATABASE"])
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

    return message


@app.route("/api/challenge/delete/<id_challenge>")
def deletechallenge(id_challenge):
    conn = sqlite3.connect(app.config["DATABASE"])
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

    return message


@app.route("/api/users/create/<name>/<admin>/<password>/<hash>")
def creationuser(name, admin, password, hash):
    conn = sqlite3.connect(app.config["DATABASE"])
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO users (name, admin, password, hash)
        VALUES (?,?,?,?)
    """,
        (name, admin, password, hash),
    )

    conn.commit()
    conn.close()

    message = "Les données ont été enregistrées avec succès!"

    return message


@app.route("/api/users/change/<id_user>/<name>/<pwd>/<hash>")
def updateusers(id_user, name, pwd, hash):
    conn = sqlite3.connect(app.config["DATABASE"])
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE users
        SET name = (?),password = (?),hash = (?)
        WHERE id_user = (?);

    """,
        (name, pwd, hash, id_user),
    )

    conn.commit()
    conn.close()

    message = "Les changements ont été enregistrés avec succès!"

    return message


@app.route("/api/users/<id_user>")
def user_json(id_user):
    conn = sqlite3.connect(app.config["DATABASE"])
    cur = conn.cursor()
    cur.execute(f"""SELECT * FROM users where id_challenge = {id_user};""")
    info = cur.fetchall()
    conn.close()
    # print(info, file=sys.stderr)
    return jsonify(info)


@app.route("/api/users/all")
def all_users():
    conn = sqlite3.connect(app.config["DATABASE"])
    cur = conn.cursor()
    cur.execute(f"""SELECT id_user,name FROM users;""")
    info = cur.fetchall()
    conn.close()
    # print(info, file=sys.stderr)
    return jsonify(info)


@app.route("/api/challenge/<id_challenge>")
def challenge_json(id_challenge):
    conn = sqlite3.connect(app.config["DATABASE"])
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
    conn = sqlite3.connect(app.config["DATABASE"])
    cur = conn.cursor()
    cur.execute(
        f"""SELECT * FROM validations where (id_user = {id_user}) and (id_challenge = {id_challenge});""",
    )
    info = cur.fetchall()
    conn.close()
    # print(info, file=sys.stderr)
    return jsonify(info)


@app.route("/allusers")
def index():
    # Effectuer la requête API pour récupérer des données au format JSON
    api_url = "http://127.0.0.1:5000/api/users/all"
    response = requests.get(api_url)

    # Vérifier si la requête a réussi (statut 200)
    if response.status_code == 200:
        data_json = response.json()
        return render_template("allusers.html", data=data_json)
    else:
        return "Erreur lors de la récupération des données de l'API"


@app.route("/api/users/delete/<id_user>")
def deleteuser(id_user):
    conn = sqlite3.connect(app.config["DATABASE"])
    cur = conn.cursor()
    cur.execute(
        """
        DELETE FROM users
        WHERE id_user = (?);
        """,
        (id_user),
    )
    cur.execute(
        """
        DELETE FROM validations
        WHERE id_user = (?);
        """,
        (id_user),
    )

    conn.commit()
    conn.close()

    message = "Les changements ont été enregistrés avec succès!"

    return message


if __name__ == "__main__":
    app.run(debug=True)

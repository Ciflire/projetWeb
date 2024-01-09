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


def get_db():
    db = sqlite3.connect(app.config["DATABASE"])
    db.row_factory = sqlite3.Row
    return db


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, "sqlite_db"):
        g.sqlite_db.close()


class User(UserMixin):
    def __init__(
        self,
        user_id: int,
        name: str,
        is_admin: int,
        password: str,
    ):
        self.user_id = user_id
        self.name = name
        self.is_admin = is_admin
        self.password = password

    def __str__(self):
        return "{0}".format(self.name)

    def serialize(self):
        """Méthode de formatage pour ajouter les données dans la DB"""
        return (
            self.user_id,
            self.name,
            self.is_admin,
            self.password,
        )

    def get_id(self):  # necessary for flask_login
        return self.user_id


@login_manager.user_loader
def load_user(user_id: int):
    cursor = get_db().cursor()
    cursor.execute(
        "SELECT id_user, name, admin, hash FROM users WHERE id_user = ?",
        (user_id,),
    )
    db_data = cursor.fetchone()
    if db_data is not None:
        client = User(*db_data)
        return client
    return None


@app.route("/register", methods=("GET", "POST"))
def register():
    if request.method == "POST":
        name = request.form["username"]
        password = request.form["password"]
        password_confirm = request.form["confirm_password"]
        conn = get_db()
        cursor = conn.cursor()
        if password != password_confirm:  # passwords do not match
            return render_template(
                "popup.html",
                message="Les mots de passe ne correspondent pas.",
            )
        hashed_pass = generate_password_hash(password)
        cursor.execute(
            "INSERT INTO users (name, admin, hash) VALUES (?,1,?)",
            (name, hashed_pass),
        )
        conn.commit()
        return redirect(url_for("login"))
    return render_template("register.html")


@app.route("/login/", methods=("GET", "POST"))
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id_user, name, admin, hash FROM users WHERE name = ?",
            (username,),
        )
        user = cursor.fetchone()
        if user is None:
            return render_template(
                "popup.html",
                message="Cette adresse email n'est liée à aucun compte.",
            )

        client = User(*user)
        if not check_password_hash(client.password, password):
            return render_template(
                "popup.html", message="Le mot de passe est incorrect."
            )
        login_user(client)
        return redirect(url_for("home"))
    else:
        return render_template("login.html")


@app.route("/logout/")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))


def generateToken() -> str:
    token = secrets.token_hex(16)
    return token


# accueil
@app.route("/")
def home():
    return render_template("accueil.html")


@app.route("/challenge/create")
def challengecreate():
    return render_template("admincreachallenge.html")


@app.route("/challenge/delete")
def challengedelete():
    return render_template("admindeletechallenge.html")


@app.route("/challenge/modify")
def challengemodify():
    return render_template("adminmodifchallenge.html")


@app.route("/challenge/all")
def challengeall():
    return render_template("allchallenge.html")


@app.route("/challenge/all/admin")
def challengealladmin():
    return render_template("allchallengeadmin.html")


@app.route("/users/all")
def usersall():
    return render_template("allusers.html")


@app.route("/challenge")
def challenge():
    return render_template("challenge.html")


@app.route("/challenge/admin")
def challengeadmin():
    return render_template("challengeadmin.html")


@app.route("/challenge/add/user")
def challengeadduser():
    return render_template("challengeadminadduser.html")


@app.route("/challenge/register")
def challengeregister():
    return render_template("challengeregiste.html")


@app.route("/challenge/user")
def challengeuser():
    return render_template("mychallenge.html")


@app.route("/user")
def user():
    return render_template("myprofil.html")


@app.route("/challenge/delete")
def deletechallenge():
    return render_template("admindeletechallenge.html")


@app.route("/user/modify")
def usermodify():
    return render_template("usermodifprofil.html")


@app.route("/template")
def template():
    return render_template("template.html")


# all challenge admin remove

# admin Create challenge
# admin modify challenge
# challenge admin
# challenge admin add user
# challenge registre


@app.route("/createchallenge")
def createchallenge():
    return render_template("createchallenge.html")


@app.route("/api/challenge/create", methods=["POST"])
def apichallengecreate():
    creation_date = datetime.now().timestamp()
    print(request.form, file=sys.stderr)
    name = request.form["namechallenge"]
    end_date = request.form["date"]

    # Convert the string to a datetime object
    date_object = datetime.strptime(end_date, "%Y-%m-%d")

    # Get the timestamp (seconds since the epoch)
    end_date = date_object.timestamp()
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
def apiChallengeModify(id_challenge, name, end_date):
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
def apiChallengeDelete(id_challenge):
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
def apiUserCreate(name, admin, password, hash):
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
def apiUserModify(id_user, name, pwd, hash):
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
def apiUser(id_user):
    conn = sqlite3.connect(app.config["DATABASE"])
    cur = conn.cursor()
    cur.execute(f"""SELECT * FROM users where id_challenge = {id_user};""")
    info = cur.fetchall()
    conn.close()
    # print(info, file=sys.stderr)
    return jsonify(info)


@app.route("/api/users/all")
def apiUserAll():
    conn = sqlite3.connect(app.config["DATABASE"])
    cur = conn.cursor()
    cur.execute("""SELECT id_user,name FROM users;""")
    info = cur.fetchall()
    conn.close()
    # print(info, file=sys.stderr)
    return jsonify(info)


@app.route("/api/challenge/<id_challenge>")
def apiChallenge(id_challenge):
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
def apiValidation(id_user, id_challenge):
    conn = sqlite3.connect(app.config["DATABASE"])
    cur = conn.cursor()
    cur.execute(
        f"""SELECT * FROM validations where (id_user = {id_user}) and (id_challenge = {id_challenge});""",
    )
    info = cur.fetchall()
    conn.close()
    # print(info, file=sys.stderr)
    return jsonify(info)


@app.route("/api/users/delete/<id_user>")
def apiUserDelete(id_user):
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

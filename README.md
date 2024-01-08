# [Nom du projet]

## Setup

Clonez le dépôt puis rendez vous dans le dossier cloné

```sh
git clone git@gitlab.telecomnancy.univ-lorraine.fr:ppii-fisa/projet.git
cd projet
```

Créez un environnement python pour lancer le projet et installez les dépendances nécessaire:

```sh
python -m venv env
source env/bin/activate
pip install -r requirements.txt
```

Pour la database, il est fourni un fichier `schema.sql`, il vous est fourni ci-après un exemple d'une succession de commande à executer, à adapter à votre convenance. À savoir qu'il faut que votre databse se trouver dans le dossier static

```sh
cd static
touch database.db
sqlite3 database.db < ../schema.sql
```

Une fois l'installation terminée, lancez le script `run.sh` en pensant à le rendre executable au préalable

```sh
chmod +x run.sh
./run.sh
```

Le projet tourne désormais en local, vous pouvez accéder au pages via l'adresse: https://127.0.0.1:5000/

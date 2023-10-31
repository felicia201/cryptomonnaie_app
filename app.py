from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
import mysql.connector
import requests
import time
import threading
import secrets

app = Flask(__name__, template_folder='templates')

# Établir une connexion à la base de données MySQL
connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="app_py"
)
cursor = connection.cursor()

app.secret_key = secrets.token_hex(16)  # Remplacez par votre clé secrète

# Créez un objet LoginManager
login_manager = LoginManager()
login_manager.login_view = "login"  # Redirigez l'utilisateur vers la page de connexion s'il n'est pas connecté
login_manager.init_app(app)

# Configuration de la base de données MySQL
app.config[
    'SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/app_py'  # Remplacez les informations de connexion à MySQL
db = SQLAlchemy(app)
login_manager = LoginManager(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user)  # Utilisez login_user pour connecter l'utilisateur
            flash("Connexion réussie", "success")
            return redirect(url_for("accueil"))  # Redirigez vers la page d'accueil après la connexion
        else:
            flash("Nom d'utilisateur ou mot de passe incorrect", "danger")
    return render_template("login.html")


@app.route('/dashboard')
@login_required
def dashboard():
    return 'Tableau de bord - Vous êtes connecté en tant que ' + current_user.username


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


# Variable pour stocker les alertes
alertes = []


# Page d'accueil : Afficher les alertes pour le Bitcoin depuis la base de données
@app.route("/")
def accueil():
    # Sélectionnez uniquement les alertes pour le Bitcoin (BTC)
    cursor.execute("SELECT id, cryptomonnaie, prix FROM alertes WHERE cryptomonnaie = 'BTC'")
    alertes = cursor.fetchall()
    return render_template("accueil.html", alertes=alertes)


# Fonction pour obtenir les données de prix du Bitcoin
def prix_bitcoins():
    url = "https://rest.coinapi.io/v1/exchangerate/BTC/USD"
    headers = {"X-CoinAPI-Key": "C8034E50-FAA6-4EE9-A59F-40F516E4BECF"}

    try:
        resp = requests.get(url, headers=headers)
        resp.raise_for_status()  # Vérifiez si la réponse contient une erreur HTTP

        data = resp.json()
        prix_bitcoins = data["rate"]
        return prix_bitcoins
    except requests.exceptions.RequestException as e:
        print(f"Erreur de l'API : {e}")
        return None


# Appel de la fonction pour obtenir le prix du Bitcoin
prix = prix_bitcoins()
if prix is not None:
    print(f"Prix actuel du Bitcoin en USD : {prix} $")
else:
    print("Impossible d'obtenir le prix du Bitcoin.")


# surveillance de changement de prix
def mechanism_change_prix():
    while True:  # boucle infinie pour surveiller les prix
        prix_actuel = prix_bitcoins()
        # boucle pour comparer le prix actuel avec les alertes
        for alerte in alertes:
            if prix_actuel < alerte['prix']:
                notifier_utilisateur(alerte)

        time.sleep(60)  # attendre 60s pour mettre a jour le nouveaux prix


# Fonction pour notifier l'utilisateur
def notifier_utilisateur(alerte):
    print(f"Alerte déclenchée : Le prix du {alerte['cryptomonnaie']} est tombé en dessous de {alerte['prix']} $.")


# Page pour créer une nouvelle alerte pour le Bitcoin
@app.route("/creer_alerte", methods=["POST"])
def creer_alerte():
    cryptomonnaie = "BTC"  # Assurez-vous que la cryptomonnaie est définie sur BTC
    prix = request.form.get("prix")
    devise = request.form.get("devise")  # Obtenez la devise depuis la saisie de l'utilisateur
    if prix and devise:
        prix = float(prix)
        insert_alert_query = "INSERT INTO alertes (cryptomonnaie, prix, devise) VALUES (%s, %s, %s)"
        cursor.execute(insert_alert_query, (cryptomonnaie, prix, devise))
        connection.commit()
    return redirect(url_for("accueil"))


# Page pour mettre à jour une alerte existante
@app.route("/update_alerte/<int:alerte_id>", methods=["POST"])
def update_alerte(alerte_id):
    new_prix = float(request.form["nouveau_prix"])
    update_alert_query = "UPDATE alertes SET prix = %s WHERE id = %s"
    cursor.execute(update_alert_query, (new_prix, alerte_id))
    connection.commit()
    return redirect(url_for("accueil"))


# Page pour supprimer une alerte
@app.route("/supprimer_alerte/<int:alerte_id>")
def supprimer_alerte(alerte_id):
    delete_alert_query = "DELETE FROM alertes WHERE id = %s"
    cursor.execute(delete_alert_query, (alerte_id,))
    connection.commit()
    return redirect(url_for("accueil"))


if __name__ == "__main__":
    # Créez un thread pour exécuter la fonction de surveillance en continu en arrière-plan
    surveillance_thread = threading.Thread(target=mechanism_change_prix)
    surveillance_thread.daemon = True
    surveillance_thread.start()
    app.run()

from flask import Flask, render_template, request, redirect, url_for, flash,session
import mysql.connector
import requests
import time
import threading

app = Flask(__name__, template_folder='templates')
app.secret_key = 'xyzsdfg'

# Établir une connexion à la base de données MySQL
connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="app_py"
)
cursor = connection.cursor()

# Variable pour stocker les alertes
alertes = []



# Page d'accueil : Afficher les alertes pour le Bitcoin depuis la base de données
@app.route("/accueil", methods=["GET", "POST"])
def accueil():
    cryptomonnaie = request.args.get("cryptomonnaie",
                                     default="BTC")  # Récupérez la cryptomonnaie à partir de la requête
    query = "SELECT id, cryptomonnaie, prix, devise FROM alertes WHERE cryptomonnaie = %s"
    cursor.execute(query, (cryptomonnaie,))
    alertes = cursor.fetchall()
    return render_template("accueil.html", alertes=alertes, cryptomonnaie=cryptomonnaie)


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
    while True:
        prix_actuel = prix_bitcoins()
        for alerte in alertes:
            if prix_actuel * (1 - alerte['pourcentage'] / 100) <= alerte['prix']:
                notifier_utilisateur(alerte)
        time.sleep(60)


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

@app.route('/')
# Page de login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Vérifier les informations de connexion dans la base de données
        query = "SELECT id, email, password FROM users WHERE email = %s AND password = %s"
        cursor.execute(query, (email, password))
        user = cursor.fetchone()

        if user:
            # Les informations de connexion sont correctes, définir la session
            session['user_id'] = user[0]
            flash('Logged in successfully!', 'success')
            return redirect(url_for('accueil'))
        else:
            flash('Invalid email or password. Please try again.', 'error')

    return render_template('login.html')


# Page de logout
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Logged out successfully!', 'success')
    return redirect(url_for('login'))


# Page d'inscription
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        # Insérer l'utilisateur dans la base de données
        query = "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)"
        cursor.execute(query, (name, email, password))
        connection.commit()

        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


if __name__ == "__main__":
    # Créez un thread pour exécuter la fonction de surveillance en continu en arrière-plan
    surveillance_thread = threading.Thread(target=mechanism_change_prix)
    surveillance_thread.daemon = True
    surveillance_thread.start()
    app.run()

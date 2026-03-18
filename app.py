from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# page accueil
@app.route("/")
def home():
    return render_template("index.html")

# page inscription
@app.route("/register", methods=["GET","POST"])
def register():

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        print("Nouvel utilisateur :", username)

        return redirect(url_for("login"))

    return render_template("register.html")

# page connexion
@app.route("/login", methods=["GET","POST"])
def login():

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        print("Connexion :", username)

        return redirect(url_for("chat"))

    return render_template("login.html")

# page chat
@app.route("/chat")
def chat():
    return render_template("chat.html")

if __name__ == "__main__":
    app.run(debug=True)
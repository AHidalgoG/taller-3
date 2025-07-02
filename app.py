from flask import Flask, render_template, request, redirect, url_for, session, flash
from pymongo import MongoClient
from dotenv import load_dotenv
import os
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv() #se carga el archivo .env, donde se ubican las credenciales de MongoDB

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "clave-secreta-de-desarrollo")

client = MongoClient(os.getenv("MONGO_URI")) #se accede a MongoDB
db = client["foroFlask"] #se accede a la BD foroFlask dentro de las credenciales accedidas anteriormente por client
temas = db["temas"] #se accede a la colección "temas"
usuarios = db["users"] #se accede a la colección "usuarios"
count = temas.count_documents({})

@app.route("/")
def index():
    todos = temas.find()
    total = count
    nombre = session.get("nombre")
    return render_template("index.html", temas=todos, total=total, usuario=nombre) 


@app.route("/nuevo", methods=["GET", "POST"])
def nuevo_tema():
    nombre = session.get("nombre")
    if request.method == "POST":
        titulo = request.form["titulo"]
        creador = session.get("nombre")
        contenido = request.form["contenido"]
        temas.insert_one({"titulo": titulo, "creador": creador, "contenido": contenido, "respuestas": []})
        return redirect(url_for("index"))
    return render_template("nuevo_tema.html", usuario=nombre)

@app.route("/tema/<id>", methods=["GET", "POST"])
def ver_tema(id):
    tema = temas.find_one({"_id": ObjectId(id)})
    nombre = session.get("nombre")
    if request.method == "POST":
        nueva = request.form["respuesta"]
        temas.update_one(
            {"_id": ObjectId(id)},
            {"$push": {"respuestas": nueva}}
        )
        return redirect(url_for("ver_tema", id=id))

    return render_template("tema.html", tema=tema, usuario=nombre)    

@app.route('/login', methods=["POST", "GET"])
def login():
    if(request.method == "POST"):
        correo = request.form["correo"]
        clave = request.form["password"]

        usuario = usuarios.find_one({"correo": correo})
        if(usuario and check_password_hash(usuario["password"], clave)):
            session["nombre"] = usuario.get("nombre")
            return redirect(url_for("index"))
        else:
            flash("Correo o contraseña incorrecto")
            return redirect(url_for("login"))
    return render_template("login.html")

@app.route('/register', methods=["POST", "GET"])
def register():
    if(request.method == "POST"):
        nombre = request.form["nombre"]
        correo = request.form["correo"]
        password = request.form["password"]
        clave_segura = generate_password_hash(password)
        usuarios.insert_one({"nombre": nombre, "correo": correo, "password": clave_segura})
        return redirect(url_for("login"))
    return render_template("registro.html")

@app.route('/cerrar_sesion')
def logout():
    session.clear()
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.run(debug=True)
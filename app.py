from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from dotenv import load_dotenv
import os
from bson.objectid import ObjectId

load_dotenv() #se carga el archivo .env, donde se ubican las credenciales de MongoDB

app = Flask(__name__)

client = MongoClient(os.getenv("MONGO_URI")) #se accede a MongoDB
db = client["foroFlask"] #se accede a la BD foroFlask dentro de las credenciales accedidas anteriormente por client
temas = db["temas"] #se accede a la colección "temas"
usuarios = db["users"] #se accede a la colección "usuarios"
count = temas.count_documents({})

@app.route("/")
def index():
    todos = temas.find()
    total = count
    return render_template("index.html", temas=todos, total=total)

@app.route("/nuevo", methods=["GET", "POST"])
def nuevo_tema():
    if request.method == "POST":
        titulo = request.form["titulo"]
        creador = request.form["usuario"]
        contenido = request.form["contenido"]
        temas.insert_one({"titulo": titulo, "creador": creador, "contenido": contenido, "respuestas": []})
        return redirect(url_for("index"))
    return render_template("nuevo_tema.html")

@app.route("/tema/<id>", methods=["GET", "POST"])
def ver_tema(id):
    tema = temas.find_one({"_id": ObjectId(id)})

    if request.method == "POST":
        nueva = request.form["respuesta"]
        temas.update_one(
            {"_id": ObjectId(id)},
            {"$push": {"respuestas": nueva}}
        )
        return redirect(url_for("ver_tema", id=id))

    return render_template("tema.html", tema=tema)    

@app.route('/login', methods=["POST", "GET"])
def login():
    if(request.method == "POST"):
        correo = request.form["correo"]
        password = request.form["password"]
        if(correo == usuarios.find_one({correo}) and password == usuarios.find_one({password})):
            return redirect(url_for("index"))
    return render_template("login.html")

@app.route('/register', methods=["POST", "GET"])
def register():
    if(request.method == "POST"):
        nombre = request.form["nombre"]
        correo = request.form["correo"]
        password = request.form["password"]
        usuarios.insert_one({"nombre": nombre, "correo": correo, "password": password})
        return redirect(url_for("login"))
    return render_template("registro.html")



if __name__ == "__main__":
    app.run(debug=True)
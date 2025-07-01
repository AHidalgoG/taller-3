from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from dotenv import load_dotenv
import os
from bson.objectid import ObjectId

load_dotenv()

app = Flask(__name__)

client = MongoClient(os.getenv("MONGO_URI"))
db = client["foroFlask"]
temas = db["temas"]

@app.route("/")
def index():
    todos = temas.find()
    return render_template("index.html", temas=todos)

@app.route("/nuevo", methods=["GET", "POST"])
def nuevo_tema():
    if request.method == "POST":
        titulo = request.form["titulo"]
        contenido = request.form["contenido"]
        creador = request.form["creador"]
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

if __name__ == "__main__":
    app.run(debug=True)
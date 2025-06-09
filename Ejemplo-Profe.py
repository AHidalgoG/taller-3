from flask import (
    Flask, request, jsonify,
    Blueprint, render_template, redirect, url_for
)
from werkzeug.security import generate_password_hash
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime

# â€”â€”â€”â€”â€” ConfiguraciÃ³n â€”â€”â€”â€”â€”
MONGO_URI = "mongodb+srv://ceferinocastro:xxxxxxxxx@cluster0.v9txkzg.mongodb.net/foro?retryWrites=true&w=majority&appName=Cluster0"
SECRET_KEY = "desde_el_dia_en_que_yo_tevi"

# â€”â€”â€”â€”â€” InicializaciÃ³n de la app â€”â€”â€”â€”â€”
app = Flask(__name__, template_folder='templates')
app.secret_key = SECRET_KEY

# â€”â€”â€”â€”â€” ConexiÃ³n a MongoDB â€”â€”â€”â€”â€”
def get_db():
    client = MongoClient(MONGO_URI)
    return client['foro']  # Base de datos "for"

# â€”â€”â€”â€”â€” Servicios de usuario â€”â€”â€”â€”â€”
def listar_usuarios():
    db = get_db()
    users = db.usuario.find()
    return [{
        '_id': str(u['_id']),
        'username': u.get('username', ''),
        'email': u.get('email', ''),
        'rol': u.get('rol', 'usuario'),
        'fecha_creacion': u.get('fecha_creacion', datetime.utcnow()).strftime('%Y-%m-%d')
    } for u in users]


def crear_usuario(data):
    db = get_db()
    pwd_hash = generate_password_hash(data['contraseÃ±a'])
    nuevo = {
        'username': data['username'],
        'email': data['email'],
        'password_hash': pwd_hash,
        'rol': data.get('rol', 'usuario'),
        'fecha_creacion': datetime.utcnow()
    }
    res = db.usuario.insert_one(nuevo)
    return str(res.inserted_id)


def actualizar_usuario(usuario_id, campos):
    db = get_db()
    # Si se envÃ­a 'contraseÃ±a', la almacenamos como password_hash
    if 'contraseÃ±a' in campos:
        campos['password_hash'] = generate_password_hash(campos.pop('contraseÃ±a'))
    return db.usuario.update_one(
        {'_id': ObjectId(usuario_id)},
        {'$set': campos}
    )


def eliminar_usuario(usuario_id):
    db = get_db()
    res = db.usuario.delete_one({'_id': ObjectId(usuario_id)})
    return res.deleted_count

# â€”â€”â€”â€”â€” Blueprint de usuarios â€”â€”â€”â€”â€”
usuarios_bp = Blueprint('usuarios', __name__, url_prefix='/usuarios')

@usuarios_bp.route('/vista', methods=['GET'])
def vista_usuarios():
    return render_template('usuarios.html')  # Tu plantilla de gestiÃ³n

@usuarios_bp.route('/', methods=['GET'])
def api_listar():
    return jsonify(listar_usuarios())

@usuarios_bp.route('/', methods=['POST'])
def api_crear():
    data = request.get_json(force=True)
    uid = crear_usuario(data)
    return jsonify({'mensaje': 'Usuario creado', 'id': uid}), 201

@usuarios_bp.route('/<id>', methods=['PUT'])
def api_actualizar(id):
    data = request.get_json(force=True)
    res = actualizar_usuario(id, data)
    return jsonify({'mensaje': 'Usuario actualizado', 'matched': res.matched_count, 'modified': res.modified_count})

@usuarios_bp.route('/<id>', methods=['DELETE'])
def api_eliminar(id):
    deleted = eliminar_usuario(id)
    if deleted == 0:
        return jsonify({'error': 'Usuario no encontrado'}), 404
    return jsonify({'mensaje': 'Usuario eliminado', 'deleted': deleted}), 200

# Registrar blueprint y rutas generales
app.register_blueprint(usuarios_bp)

@app.route('/')
def index():
    return render_template('clase_app.html')  # Carga tu plantilla principal

@app.route('/ping')
def ping():
    return 'pong', 200

# â€”â€”â€”â€”â€” EjecuciÃ³n â€”â€”â€”â€”â€”
if __name__ == '__main__':
    app.run(debug=True)
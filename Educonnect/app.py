import sqlite3
from flask import Flask, request, jsonify, render_template, g
from flask_cors import CORS
import hashlib
import os

app = Flask(__name__)
CORS(app)

# Caminho para o banco SQLite
DATABASE = os.path.join(os.path.dirname(__file__), 'educonnect.db')

# Hashear senhas
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Conexão com o banco
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row  # Para retornar dicts em vez de tuplas
    return g.db

# Fechar conexão após requisição
@app.teardown_appcontext
def close_connection(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()

@app.route('/')
def home():
    return render_template('interface.html')

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    db = get_db()
    try:
        db.execute(
            "INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)",
            (data['name'], data['email'], hash_password(data['password']), data['user_type'])
        )
        db.commit()
        return jsonify({"success": True, "message": "Usuário cadastrado com sucesso!"})
    except Exception as e:
        return jsonify({"success": False, "message": f"Erro ao cadastrar: {str(e)}"})

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data['email']
    senha = hash_password(data['password'])
    user_type = data['user_type']

    db = get_db()
    cursor = db.execute(
        "SELECT * FROM usuarios WHERE email = ? AND senha = ? AND tipo = ?",
        (email, senha, user_type)
    )
    user = cursor.fetchone()

    if user:
        return jsonify({"success": True, "message": f"Bem-vindo(a), {user['nome']}!"})
    else:
        return jsonify({"success": False, "message": "Credenciais inválidas."})

@app.route('/listar_turmas', methods=['GET'])
def listar_turmas():
    email = request.args.get('email')
    if not email:
        return jsonify({"success": False, "message": "Email do professor não fornecido."}), 400

    db = get_db()
    cursor = db.execute(
        "SELECT nome_turma, serie, disciplina FROM turmas WHERE professor_email = ?",
        (email,)
    )
    turmas = [dict(row) for row in cursor.fetchall()]
    return jsonify({"success": True, "turmas": turmas})

@app.route('/criar_turma', methods=['POST'])
def criar_turma():
    data = request.json
    nome_turma = data.get('nome_turma')
    serie = data.get('serie')
    disciplina = data.get('disciplina')
    professor_email = data.get('professor_email')

    if not all([nome_turma, serie, disciplina, professor_email]):
        return jsonify({"success": False, "message": "Campos obrigatórios faltando."})

    db = get_db()
    try:
        db.execute("""
            INSERT INTO turmas (nome_turma, serie, disciplina, professor_email)
            VALUES (?, ?, ?, ?)
        """, (nome_turma, serie, disciplina, professor_email))
        db.commit()
        return jsonify({"success": True, "message": "Turma criada com sucesso!"})
    except Exception as e:
        return jsonify({"success": False, "message": f"Erro ao criar turma: {str(e)}"})

if __name__ == '__main__':
    app.run(debug=True)

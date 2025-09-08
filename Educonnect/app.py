from dotenv import load_dotenv
import os
from flask import Flask, request, jsonify, render_template
from flask_mysqldb import MySQL
from flask_cors import CORS
import MySQLdb.cursors
import hashlib

app = Flask(__name__)
CORS(app)
load_dotenv()
# Configurações do MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
password = os.getenv('MYSQL_PASSWORD')
app.config['MYSQL_PASSWORD'] = password
app.config['MYSQL_DB'] = 'educonnect'

mysql = MySQL(app)

# Função auxiliar para hashear senhas
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()
@app.route('/')
def home():
    return render_template('interface.html')

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    cursor = mysql.connection.cursor()
    try:
        cursor.execute("INSERT INTO usuarios (nome, email, senha, tipo) VALUES (%s, %s, %s, %s)", (
            data['name'],
            data['email'],
            hash_password(data['password']),
            data['user_type']
        ))
        mysql.connection.commit()
        return jsonify({"success": True, "message": "Usuário cadastrado com sucesso!"})
    except Exception as e:
        return jsonify({"success": False, "message": "Erro ao cadastrar: " + str(e)})

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    print("Dados recebidos para login:", data)  # ← Print para debug
    email = data['email']
    senha = hash_password(data['password'])
    user_type = data['user_type']

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM usuarios WHERE email=%s AND senha=%s AND tipo=%s", (email, senha, user_type))
    user = cursor.fetchone()
    print("Resultado do SELECT:", user)  # ← Verifica se encontrou algo

    if user:
        return jsonify({"success": True, "message": f"Bem-vindo(a), {user['nome']}!"})
    else:
        return jsonify({"success": False, "message": "Credenciais inválidas."})

@app.route('/listar_turmas', methods=['GET'])
def listar_turmas():
    email = request.args.get('email')

    if not email:
        return jsonify({"success": False, "message": "Email do professor não fornecido."}), 400

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(
        "SELECT nome_turma, serie, disciplina FROM turmas WHERE professor_email = %s",
        (email,)
    )
    turmas = cursor.fetchall()
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

    cursor = mysql.connection.cursor()
    try:
        cursor.execute("""
            INSERT INTO turmas (nome_turma, serie, disciplina, professor_email)
            VALUES (%s, %s, %s, %s)
        """, (nome_turma, serie, disciplina, professor_email))
        mysql.connection.commit()
        return jsonify({"success": True, "message": "Turma criada com sucesso!"})
    except Exception as e:
        return jsonify({"success": False, "message": f"Erro ao criar turma: {str(e)}"})


if __name__ == '__main__':
    app.run(debug=True)

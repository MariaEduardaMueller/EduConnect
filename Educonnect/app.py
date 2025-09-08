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


if __name__ == '__main__':
    app.run(debug=True)

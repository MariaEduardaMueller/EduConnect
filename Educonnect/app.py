
import sqlite3
from flask import Flask, request, jsonify, render_template, g, redirect, url_for, session
from flask_cors import CORS
import hashlib
import os


CORS()
app = Flask(__name__)
app.secret_key = 'educonnect_secret_key'
# Caminho para o banco SQLite
def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login_page'))
        return f(*args, **kwargs)
    return decorated_function
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


        # Garantir que a tabela de mensagens exista (evita erros quando falta a tabela)
        try:
            g.db.execute('''
                CREATE TABLE IF NOT EXISTS mensagens (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    remetente TEXT,
                    destinatario TEXT,
                    mensagem TEXT,
                    data_envio TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            g.db.commit()
        except Exception:
            # Se houver qualquer erro ao criar a tabela, apenas ignore aqui;
            # as rotas farão tratamento adequado quando tentarem acessar a tabela.
            pass
        
    return g.db

# Fechar conexão após requisição
@app.teardown_appcontext
def close_connection(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()


# @app.route('/')
# def index():



@app.route('/home')
@login_required
def home():
  ##  return render_template('notificacao.html')

  ##  return render_template('paginainicial.html')

    return render_template('dashboard.html')

@app.route('/login')
def login_page():  
    return render_template('login.html')


@app.route('/turmas')
@login_required
def turmas():
    db = get_db()
    email = session.get('user_email')
    cursor = db.execute(
        "SELECT nome_turma, serie, disciplina, sala FROM turmas WHERE professor_email = ?",
        (email,)
    )
    turmas = [dict(row) for row in cursor.fetchall()]
    return render_template('turmas.html', turmas=turmas)


@app.route('/atividades')
@login_required
def atividades():
    return render_template('atividades.html')


@app.route('/biblioteca')
@login_required
def biblioteca():
    return render_template('biblioteca.html')


@app.route('/horarios')
@login_required
def horarios():
    return render_template('horarios.html')


@app.route('/notas')
@login_required
def notas():
    return render_template('notas.html')

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
        session['logged_in'] = True
        session['user_email'] = email
        session['user_type'] = user_type
        return jsonify({"success": True, "message": f"Bem-vindo(a), {user['nome']}!"})
    else:
        return jsonify({"success": False, "message": "Credenciais inválidas."})
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route("/notificacoes")
def notificacoes():
    return render_template("notificacoes.html")

@app.route("/documentos")
def documentos():
    return render_template("documentos.html")


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
    sala = data.get('sala')  # Novo campo

    if not all([nome_turma, serie, disciplina, professor_email]):
        return jsonify({"success": False, "message": "Campos obrigatórios faltando."})

    db = get_db()
    try:
        db.execute("""
            INSERT INTO turmas (nome_turma, serie, disciplina, professor_email, sala)
            VALUES (?, ?, ?, ?, ?)
        """, (nome_turma, serie, disciplina, professor_email, sala))
        db.commit()
        return jsonify({"success": True, "message": "Turma criada com sucesso!"})
    except Exception as e:
        return jsonify({"success": False, "message": f"Erro ao criar turma: {str(e)}"})
@app.route('/criar_evento', methods=['POST'])
def criar_evento():
    data = request.json
    titulo = data.get('titulo')
    descricao = data.get('descricao')
    data_evento = data.get('data')
    hora = data.get('hora')
    professor_email = data.get('professor_email')

    if not all([titulo, descricao, data_evento, hora, professor_email]):
        return jsonify({"success": False, "message": "Todos os campos são obrigatórios."})

    db = get_db()
    try:
        db.execute("""
            INSERT INTO eventos (titulo, descricao, data, hora, professor_email)
            VALUES (?, ?, ?, ?, ?)
        """, (titulo, descricao, data_evento, hora, professor_email))
        db.commit()
        return jsonify({"success": True, "message": "Evento criado com sucesso!"})
    except Exception as e:
        return jsonify({"success": False, "message": f"Erro ao criar evento: {str(e)}"})



# Rotas para chat suspenso via AJAX
@app.route('/api/chat/mensagens', methods=['GET'])
@login_required
def api_chat_mensagens():
    db = get_db()
    user_email = session.get('user_email', 'anonimo')
    chat_user = request.args.get('chat_user', 'geral')
    try:
        if chat_user == 'geral':
            cursor = db.execute("SELECT remetente, mensagem, data_envio FROM mensagens WHERE destinatario = 'professor' ORDER BY data_envio DESC LIMIT 20")
        else:
            cursor = db.execute(
                "SELECT remetente, mensagem, data_envio FROM mensagens WHERE (remetente = ? AND destinatario = ?) OR (remetente = ? AND destinatario = ?) ORDER BY data_envio DESC LIMIT 20",
                (user_email, chat_user, chat_user, user_email)
            )
        mensagens = [dict(row) for row in cursor.fetchall()][::-1]
    except Exception as e:
        print('Erro em api_chat_mensagens:', e)
        mensagens = []
    return jsonify(mensagens)

@app.route('/api/chat/enviar', methods=['POST'])
@login_required
def api_chat_enviar():
    db = get_db()
    remetente = session.get('user_email', 'anonimo')
    data = request.get_json()
    mensagem = data.get('mensagem')
    destinatario = data.get('destinatario', 'professor')
    if mensagem:
        try:
            db.execute(
                "INSERT INTO mensagens (remetente, destinatario, mensagem) VALUES (?, ?, ?)",
                (remetente, destinatario, mensagem)
            )
            db.commit()
            return jsonify({'success': True})
        except Exception as e:
            print('Erro em api_chat_enviar:', e)
            return jsonify({'success': False, 'error': str(e)})
    return jsonify({'success': False, 'error': 'Mensagem vazia'})


@app.route('/api/chat/usuarios', methods=['GET'])
@login_required
def api_chat_usuarios():
    db = get_db()
    try:
        current = session.get('user_email')
        cursor = db.execute("SELECT nome, email FROM usuarios WHERE email != ?", (current,))
        usuarios = [dict(row) for row in cursor.fetchall()]
    except Exception as e:
        print('Erro em api_chat_usuarios:', e)
        usuarios = []
    return jsonify(usuarios)
@app.route('/chat', methods=['GET', 'POST'])
@login_required
def chat():
    db = get_db()
    user_email = session.get('user_email', 'anonimo')
    chat_user = request.args.get('chat_user', 'geral')

    # Envio de mensagem
    if request.method == 'POST':
        remetente = user_email
        destinatario = request.form.get('destinatario', 'professor')
        mensagem = request.form.get('mensagem')
        if mensagem:
            db.execute(
                "INSERT INTO mensagens (remetente, destinatario, mensagem) VALUES (?, ?, ?)",
                (remetente, destinatario, mensagem)
            )
            db.commit()
        # Redireciona para manter o chat selecionado
        return redirect(url_for('chat', chat_user=destinatario if destinatario != 'professor' else 'geral'))

    # Buscar lista de usuários (exceto o próprio)
    try:
        usuarios = db.execute("SELECT nome, email FROM usuarios").fetchall()
    except Exception:
        usuarios = []

    # Filtrar mensagens
    try:
        if chat_user == 'geral':
            # Chat geral: mensagens enviadas para 'professor'
            cursor = db.execute("SELECT remetente, destinatario, mensagem, data_envio FROM mensagens WHERE destinatario = 'professor' ORDER BY data_envio ASC")
        else:
            # Chat individual: mensagens entre usuário logado e o selecionado
            cursor = db.execute("SELECT remetente, destinatario, mensagem, data_envio FROM mensagens WHERE (remetente = ? AND destinatario = ?) OR (remetente = ? AND destinatario = ?) ORDER BY data_envio ASC",
                (user_email, chat_user, chat_user, user_email))
        mensagens = cursor.fetchall()
    except Exception as e:
        # Em caso de erro no DB, logamos (print) e retornamos listas vazias para não quebrar a view
        print('Erro ao buscar mensagens:', e)
        mensagens = []

    return render_template('chat.html', mensagens=mensagens, usuarios=usuarios, chat_user=chat_user)
    #fim do chat


if __name__ == '__main__':
    app.run(debug=True)

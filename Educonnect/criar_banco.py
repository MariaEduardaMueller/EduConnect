import sqlite3
import os
import sqlite3

# Caminho para o banco de dados (ajuste se estiver em outro local)
DATABASE = 'educonnect.db'

conn = sqlite3.connect(DATABASE)
cursor = conn.cursor()

try:
    cursor.execute("ALTER TABLE turmas ADD COLUMN sala TEXT")
    conn.commit()
    print("Coluna 'sala' adicionada com sucesso.")
except Exception as e:
    print("Erro ao adicionar coluna:", e)

conn.close()


'''
# Caminho para o banco de dados
DATABASE = os.path.join(os.path.dirname(__file__), 'educonnect.db')

# Conexão com o banco
conn = sqlite3.connect(DATABASE)
cursor = conn.cursor()

# Comando para criar a tabela
cursor.execute("""
CREATE TABLE IF NOT EXISTS eventos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo TEXT NOT NULL,
    descricao TEXT NOT NULL,
    data TEXT NOT NULL,
    hora TEXT NOT NULL,
    professor_email TEXT NOT NULL
);
""")

# Confirmar e fechar
conn.commit()
conn.close()

print("Tabela 'eventos' criada com sucesso.")
'''
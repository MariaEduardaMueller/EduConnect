import sqlite3

conn = sqlite3.connect('educonnect.db')
cursor = conn.cursor()

# Exemplo de tabelas — adapte ao seu .sql
cursor.execute('''
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT,
    email TEXT UNIQUE,
    senha TEXT,
    tipo TEXT
);
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS turmas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome_turma TEXT,
    serie TEXT,
    disciplina TEXT,
    professor_email TEXT
);
''')

conn.commit()
conn.close()

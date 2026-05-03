import sqlite3
from config import DB_NAME, UPLOAD_DIR, ADMIN_USUARIO, ADMIN_SENHA_HASH
import os

def get_connection():
    return sqlite3.connect(DB_NAME, check_same_thread=False)

def execute_query(query, params=(), fetch=False, fetchone=False):
    with get_connection() as conn:
        conn.execute("PRAGMA journal_mode=WAL")
        cursor = conn.cursor()
        cursor.execute(query, params)
        if fetch:
            return cursor.fetchall()
        if fetchone:
            return cursor.fetchone()
        conn.commit()

def init_db():
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    
    queries = [
        # Tabela de usuários (substitui login fixo)
        '''CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            senha_hash TEXT NOT NULL,
            nome TEXT,
            ativo INTEGER DEFAULT 1
        )''',
        # Clientes com soft delete
        '''CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            telefone TEXT,
            mensalidade REAL,
            vencimento TEXT,
            idade INTEGER,
            nivel TEXT,
            objetivo TEXT,
            agachamento_1rm REAL,
            supino_1rm REAL,
            terra_1rm REAL,
            pegada_direita REAL,
            pegada_esquerda REAL,
            historico TEXT,
            ativo INTEGER DEFAULT 1
        )''',
        # Pagamentos
        '''CREATE TABLE IF NOT EXISTS pagamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER,
            data TEXT,
            valor REAL,
            status TEXT,
            forma TEXT,
            observacao TEXT,
            FOREIGN KEY (cliente_id) REFERENCES clientes (id)
        )''',
        # Avaliações físicas
        '''CREATE TABLE IF NOT EXISTS avaliacao_fisica (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER,
            data TEXT,
            peso REAL,
            altura REAL,
            torax REAL,
            cintura REAL,
            abdomen REAL,
            quadril REAL,
            braco_direito REAL,
            braco_esquerdo REAL,
            coxa_direita REAL,
            coxa_esquerda REAL,
            panturrilha_direita REAL,
            panturrilha_esquerda REAL,
            triceps REAL,
            subescapular REAL,
            peitoral REAL,
            axilar_media REAL,
            suprailiaca REAL,
            abdominal REAL,
            coxa REAL,
            biceps REAL,
            perna REAL,
            observacoes TEXT,
            FOREIGN KEY (cliente_id) REFERENCES clientes (id)
        )''',
        # Avaliação postural
        '''CREATE TABLE IF NOT EXISTS avaliacao_postural (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER,
            data TEXT,
            vista_anterior TEXT,
            vista_posterior TEXT,
            vista_lateral_direita TEXT,
            vista_lateral_esquerda TEXT,
            cabeca TEXT,
            ombros TEXT,
            coluna TEXT,
            quadril TEXT,
            joelhos TEXT,
            pes TEXT,
            observacoes TEXT,
            FOREIGN KEY (cliente_id) REFERENCES clientes (id)
        )''',
        # Fotos (agora salva em disco, path no banco)
        '''CREATE TABLE IF NOT EXISTS fotos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER,
            data TEXT,
            tipo TEXT,
            foto_path TEXT,
            FOREIGN KEY (cliente_id) REFERENCES clientes (id)
        )''',
    ]
    for q in queries:
        execute_query(q)
    
    # Cria usuário admin se não existir
    admin_existe = execute_query("SELECT id FROM usuarios WHERE username = ?", (ADMIN_USUARIO,), fetchone=True)
    if not admin_existe:
        execute_query("INSERT INTO usuarios (username, senha_hash, nome) VALUES (?, ?, ?)",
                      (ADMIN_USUARIO, ADMIN_SENHA_HASH, "Administrador"))

init_db()
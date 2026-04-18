import psycopg2
import bcrypt
import os
import random
import string
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"), 
    "port": os.getenv("DB_PORT", "5432")
}

def conectar():
    return psycopg2.connect(**DB_CONFIG, sslmode='require')

def inicializar_banco():
    conn = conectar()
    conn.autocommit = True
    cursor = conn.cursor()
    
    # 1. Tabela de Utilizadores
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            senha_hash VARCHAR(255) NOT NULL,
            hwid VARCHAR(255),
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    # Tenta adicionar colunas caso a tabela já exista
    try: cursor.execute("ALTER TABLE usuarios ADD COLUMN hwid VARCHAR(255)")
    except: pass
    try: cursor.execute("ALTER TABLE usuarios ADD COLUMN email VARCHAR(255)")
    except: pass
    
    # 2. Tabela de Licenças (Keys)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS licencas (
            id SERIAL PRIMARY KEY,
            chave VARCHAR(50) UNIQUE NOT NULL,
            dias_validade INT NOT NULL,
            usada BOOLEAN DEFAULT FALSE,
            usuario_id INT REFERENCES usuarios(id),
            data_ativacao TIMESTAMP,
            data_expiracao TIMESTAMP,
            mp_id VARCHAR(100) UNIQUE
        )
    """)
    try: cursor.execute("ALTER TABLE licencas ADD COLUMN mp_id VARCHAR(100) UNIQUE")
    except: pass
    
    cursor.close()
    conn.close()

# ==========================================================
# MÓDULOS DE AUTENTICAÇÃO
# ==========================================================
def registrar_usuario(username, senha, email=""):
    """Regista o utilizador e guarda o e-mail na base de dados."""
    conn = conectar()
    cursor = conn.cursor()
    try:
        senha_hash = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        cursor.execute("INSERT INTO usuarios (username, senha_hash, email) VALUES (%s, %s, %s)", (username, senha_hash, email))
        conn.commit()
        return True, "Registo efetuado com sucesso!"
    except psycopg2.errors.UniqueViolation:
        return False, "Este nome de utilizador já existe."
    except Exception as e:
        return False, f"Erro: {e}"
    finally:
        cursor.close()
        conn.close()

def validar_login(username, senha, hwid_atual):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT id, senha_hash, hwid FROM usuarios WHERE username = %s", (username,))
    resultado = cursor.fetchone()
    
    if resultado:
        user_id, senha_hash_db, hwid_db = resultado
        if bcrypt.checkpw(senha.encode('utf-8'), senha_hash_db.encode('utf-8')):
            if hwid_db is None or hwid_db == "":
                cursor.execute("UPDATE usuarios SET hwid = %s WHERE id = %s", (hwid_atual, user_id))
                conn.commit()
            elif hwid_db != hwid_atual:
                cursor.close(); conn.close()
                return False, None, "🔒 ACESSO NEGADO: Esta conta está vinculada a outro Computador."
            
            cursor.close(); conn.close()
            return True, user_id, "Login efetuado!"
            
    cursor.close(); conn.close()
    return False, None, "Usuário ou senha incorretos."

def validar_login_web(username, senha):
    conn = conectar()
    cursor = conn.cursor()
    # Adicionámos a busca do e-mail também para o login
    cursor.execute("SELECT id, senha_hash, email FROM usuarios WHERE username = %s", (username,))
    resultado = cursor.fetchone()
    
    if resultado:
        user_id, senha_hash_db, email = resultado
        if bcrypt.checkpw(senha.encode('utf-8'), senha_hash_db.encode('utf-8')):
            cursor.close(); conn.close()
            return True, user_id, email, "Login web efetuado!"
            
    cursor.close(); conn.close()
    return False, None, None, "Usuário ou senha incorretos."

# ==========================================================
# MÓDULOS DE LICENÇAS E COMPRAS
# ==========================================================
def gerar_key_compra(user_id, dias, mp_id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT chave FROM licencas WHERE mp_id = %s", (str(mp_id),))
    existente = cursor.fetchone()
    if existente:
        cursor.close(); conn.close()
        return existente[0]
    pedacos = [''.join(random.choices(string.ascii_uppercase + string.digits, k=4)) for _ in range(4)]
    nova_chave = '-'.join(pedacos)
    cursor.execute("INSERT INTO licencas (chave, dias_validade, usuario_id, usada, mp_id) VALUES (%s, %s, %s, FALSE, %s)", (nova_chave, dias, user_id, str(mp_id)))
    conn.commit()
    cursor.close(); conn.close()
    return nova_chave

def verificar_licenca_ativa(user_id):
    conn = conectar()
    cursor = conn.cursor()
    agora = datetime.now()
    cursor.execute("""
        SELECT data_expiracao FROM licencas 
        WHERE usuario_id = %s AND usada = TRUE AND data_expiracao > %s
        ORDER BY data_expiracao DESC LIMIT 1
    """, (user_id, agora))
    resultado = cursor.fetchone()
    cursor.close(); conn.close()
    if resultado:
        dias_restantes = (resultado[0] - agora).days
        if dias_restantes <= 0: dias_restantes = 1 
        return True, dias_restantes
    return False, 0

def ativar_key(user_id, chave):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT id, dias_validade FROM licencas WHERE chave = %s AND usada = FALSE", (chave,))
    resultado = cursor.fetchone()
    if not resultado:
        cursor.close(); conn.close()
        return False, "Key inválida, incorreta ou já utilizada."
    licenca_id, dias = resultado
    agora = datetime.now()
    expiracao = agora + timedelta(days=dias)
    cursor.execute("UPDATE licencas SET usada = TRUE, usuario_id = %s, data_ativacao = %s, data_expiracao = %s WHERE id = %s", (user_id, agora, expiracao, licenca_id))
    conn.commit()
    cursor.close(); conn.close()
    return True, f"✅ O seu Plano de {dias} dias foi ativado com sucesso!"

def obter_perfil_usuario(user_id):
    conn = conectar()
    cursor = conn.cursor()
    agora = datetime.now()
    cursor.execute("SELECT dias_validade, data_expiracao FROM licencas WHERE usuario_id = %s AND usada = TRUE AND data_expiracao > %s ORDER BY data_expiracao DESC LIMIT 1", (user_id, agora))
    licenca_ativa = cursor.fetchone()
    dias_restantes = 0
    status_plano = "Nenhum plano ativo"
    if licenca_ativa:
        dias_restantes = (licenca_ativa[1] - agora).days
        if dias_restantes <= 0: dias_restantes = 1
        status_plano = f"Plano VIP ({licenca_ativa[0]} Dias)"
    cursor.execute("SELECT chave, dias_validade, usada, data_ativacao FROM licencas WHERE usuario_id = %s ORDER BY id DESC LIMIT 10", (user_id,))
    historico = []
    for linha in cursor.fetchall():
        historico.append({"chave": linha[0], "plano": f"{linha[1]} Dias", "status": "Ativa" if linha[2] else "Aguardando Uso", "data": linha[3].strftime("%d/%m/%Y") if linha[3] else "N/A"})
    cursor.execute("SELECT username FROM usuarios WHERE id = %s", (user_id,))
    username = cursor.fetchone()[0]
    cursor.close(); conn.close()
    return {"username": username, "dias_restantes": dias_restantes, "status_plano": status_plano, "historico": historico}

try: inicializar_banco()
except Exception as e: print(f"Aviso ao iniciar BD: {e}")
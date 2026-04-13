import psycopg2
import bcrypt
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Carrega as variáveis de segurança do arquivo .env
load_dotenv()

# ==========================================================
# CREDENCIAIS PUXADAS DE FORMA SEGURA (SEM EXPOR NO CÓDIGO)
# ==========================================================
DB_CONFIG = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"), 
    "port": os.getenv("DB_PORT", "5432")
}

def conectar():
    return psycopg2.connect(**DB_CONFIG)

def inicializar_banco():
    conn = conectar()
    conn.autocommit = True # Permite executar o ALTER TABLE de forma segura
    cursor = conn.cursor()
    
    # Tabela de Utilizadores (Agora com a coluna HWID)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            senha_hash VARCHAR(255) NOT NULL,
            hwid VARCHAR(255),
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Se a tabela já existir de um teste anterior, tenta adicionar a coluna HWID sem apagar os dados
    try:
        cursor.execute("ALTER TABLE usuarios ADD COLUMN hwid VARCHAR(255)")
    except Exception:
        pass # A coluna já existe, segue em frente
    
    # Tabela de Keys
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS licencas (
            id SERIAL PRIMARY KEY,
            chave VARCHAR(50) UNIQUE NOT NULL,
            dias_validade INT NOT NULL,
            usada BOOLEAN DEFAULT FALSE,
            usuario_id INT REFERENCES usuarios(id),
            data_ativacao TIMESTAMP,
            data_expiracao TIMESTAMP
        )
    """)
    
    cursor.close()
    conn.close()

def registrar_usuario(username, senha):
    conn = conectar()
    cursor = conn.cursor()
    try:
        senha_hash = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        cursor.execute("INSERT INTO usuarios (username, senha_hash) VALUES (%s, %s)", (username, senha_hash))
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
    """Valida a senha e trava/verifica o HWID da máquina (3 argumentos)."""
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT id, senha_hash, hwid FROM usuarios WHERE username = %s", (username,))
    resultado = cursor.fetchone()
    
    if resultado:
        user_id, senha_hash_db, hwid_db = resultado
        
        # Verifica a Senha
        if bcrypt.checkpw(senha.encode('utf-8'), senha_hash_db.encode('utf-8')):
            
            # Verifica o HWID
            if hwid_db is None or hwid_db == "":
                # 1º Login da conta: Regista o HWID deste PC para sempre!
                cursor.execute("UPDATE usuarios SET hwid = %s WHERE id = %s", (hwid_atual, user_id))
                conn.commit()
            elif hwid_db != hwid_atual:
                # O utilizador está a tentar abrir noutro PC
                cursor.close(); conn.close()
                return False, None, "🔒 ACESSO NEGADO: Esta conta está vinculada a outro Computador (HWID Inválido)."
            
            cursor.close(); conn.close()
            return True, user_id, "Login efetuado!"
            
    cursor.close(); conn.close()
    return False, None, "Usuário ou senha incorretos."

def verificar_licenca_ativa(user_id):
    """Retorna True e a quantidade de dias restantes se a Key for válida."""
    conn = conectar()
    cursor = conn.cursor()
    agora = datetime.now()
    
    # Pega a licença ativa com a maior data de expiração
    cursor.execute("""
        SELECT data_expiracao FROM licencas 
        WHERE usuario_id = %s AND usada = TRUE AND data_expiracao > %s
        ORDER BY data_expiracao DESC LIMIT 1
    """, (user_id, agora))
    
    resultado = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if resultado:
        data_expiracao = resultado[0]
        dias_restantes = (data_expiracao - agora).days
        
        # Se expirar em menos de 24h, mostra 1 dia.
        if dias_restantes == 0: dias_restantes = 1 
        
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
    
    # Calcula a data exata de expiração baseada no plano da Key
    expiracao = agora + timedelta(days=dias)
    
    cursor.execute("""
        UPDATE licencas 
        SET usada = TRUE, usuario_id = %s, data_ativacao = %s, data_expiracao = %s 
        WHERE id = %s
    """, (user_id, agora, expiracao, licenca_id))
    
    conn.commit()
    cursor.close(); conn.close()
    return True, f"✅ O seu Plano de {dias} dias foi ativado com sucesso!"

try: 
    inicializar_banco()
except Exception as e: 
    print(f"Aviso ao iniciar BD: {e}")
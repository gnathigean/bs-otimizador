from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import banco_dados
import smtplib
import os
import mercadopago
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    # Lista de extensões permitidas para evitar expor arquivos sensíveis como .env ou .py
    extensoes_permitidas = ('.js', '.css', '.png', '.jpg', '.jpeg', '.svg', '.ico', '.json')
    if path.endswith(extensoes_permitidas):
        return send_from_directory('.', path)
    return "Not Found", 404

EMAIL_REMETENTE = os.getenv("EMAIL_REMETENTE")
EMAIL_SENHA = os.getenv("EMAIL_SENHA")
MP_TOKEN = os.getenv("MP_ACCESS_TOKEN", "").strip()
sdk = mercadopago.SDK(MP_TOKEN)

def enviar_email(destinatario, assunto, corpo_html):
    if not EMAIL_REMETENTE or not EMAIL_SENHA: 
        print("Email não configurado. Ignorando envio.")
        return
    try:
        msg = MIMEMultipart()
        msg['From'] = f"BS Optimizer Pro <{EMAIL_REMETENTE}>"
        msg['To'] = destinatario
        msg['Subject'] = assunto
        msg.attach(MIMEText(corpo_html, 'html'))
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_REMETENTE, EMAIL_SENHA)
        server.send_message(msg)
        server.quit()
    except Exception as e:
        # Se a senha do Google estiver errada, avisa no terminal, mas NÃO dá crash no servidor.
        print(f"Erro ao enviar e-mail (Verifique sua Senha de App do Gmail): {e}")

@app.route('/api/auth', methods=['POST'])
def autenticar():
    dados = request.json
    usuario, senha, email_user, modo = dados.get('username'), dados.get('password'), dados.get('email', ''), dados.get('mode')
    
    if modo == 'registro':
        # Envia o e-mail para a BD
        sucesso, msg = banco_dados.registrar_usuario(usuario, senha, email_user)
        
        if sucesso and email_user: 
            corpo_email = f"""
            <div style="font-family: 'Arial', sans-serif; background-color: #07070a; color: #f8fafc; padding: 40px 20px; text-align: center; border-radius: 12px; border: 1px solid #333;">
                <h1 style="color: #8b5cf6; margin-bottom: 5px; font-size: 28px; letter-spacing: 2px;">⚡ BS OPTIMIZER</h1>
                <h2 style="color: #00e676; margin-bottom: 25px;">Bem-vindo à Elite, {usuario}!</h2>
                
                <p style="font-size: 16px; color: #94a3b8; line-height: 1.6; max-width: 500px; margin: 0 auto 30px;">
                    A sua conta foi criada com sucesso. Você acaba de dar o primeiro passo para desbloquear o verdadeiro poder do seu hardware e dominar o Blood Strike com <strong>Zero Delay e FPS Máximo</strong>.
                </p>
                
                <div style="background-color: #12121a; padding: 20px; border-radius: 8px; border: 1px solid #8b5cf6; display: inline-block; margin-bottom: 30px;">
                    <p style="margin: 0; font-size: 15px; color: #cbd5e1;">Usuário: <strong style="color: #fff;">{usuario}</strong></p>
                    <p style="margin: 5px 0 0 0; font-size: 15px; color: #cbd5e1;">E-mail: <strong style="color: #fff;">{email_user}</strong></p>
                </div>
                
                <p style="font-size: 14px; color: #94a3b8;">
                    Acesse o nosso site, escolha o seu Plano VIP e receba a sua Key de ativação instantaneamente para colar no seu aplicativo.
                </p>
                <p style="font-size: 12px; color: #555; margin-top: 40px;">
                    Este é um e-mail automático, por favor não responda.
                </p>
            </div>
            """
            enviar_email(email_user, "Conta Criada - Bem-vindo ao BS Optimizer Pro", corpo_email)
            
        return jsonify({"sucesso": sucesso, "mensagem": msg})
        
    elif modo == 'login':
        # CORREÇÃO: Agora o api.py espera receber 4 valores da função validar_login_web!
        sucesso, user_id, email_bd, msg = banco_dados.validar_login_web(usuario, senha)
        return jsonify({"sucesso": sucesso, "mensagem": msg, "user_id": user_id, "username": usuario, "email": email_bd})

@app.route('/api/perfil', methods=['POST'])
def perfil():
    user_id = request.json.get('user_id')
    if not user_id: return jsonify({"sucesso": False})
    return jsonify({"sucesso": True, "perfil": banco_dados.obter_perfil_usuario(user_id)})

@app.route('/api/comprar', methods=['POST'])
def gerar_pagamento():
    dados = request.json
    user_id = dados.get('user_id')
    plano = dados.get('plano')
    email_recebido = dados.get('email', '').strip()
    
    if not user_id: 
        return jsonify({"sucesso": False, "mensagem": "Logue-se primeiro!"})

    email_payer = email_recebido if email_recebido else "cliente@email.com"
    preco, dias = (15.00, 7) if plano == "7 Dias" else (35.00, 30)

    # Recebe os novos dados do checkout
    dados_checkout = request.json
    nome_real = dados_checkout.get("nome", "Cliente BS")
    cpf_real = str(dados_checkout.get("cpf", "")).replace(".", "").replace("-", "").strip()
    
    # Divide nome para first/last name conforme exigido pelo MP
    partes_nome = nome_real.split(" ", 1)
    p_nome = partes_nome[0]
    u_nome = partes_nome[1] if len(partes_nome) > 1 else "Optimizer Pro"

    payment_data = {
        "transaction_amount": preco,
        "description": f"Plano VIP {plano} - BS Optimizer Pro",
        "payment_method_id": "pix",
        "payer": {
            "email": email_payer, 
            "first_name": p_nome,
            "last_name": u_nome,
            "identification": { "type": "CPF", "number": cpf_real }
        },
        "external_reference": f"{user_id}_{dias}_{email_payer}"
    }

    try:
        resultado = sdk.payment().create(payment_data)
        pagamento = resultado["response"]
        
        if "id" in pagamento:
            print(f"PIX GERADO COM SUCESSO: ID {pagamento['id']} para User {user_id}")
            return jsonify({
                "sucesso": True,
                "payment_id": pagamento["id"],
                "qr_code": pagamento["point_of_interaction"]["transaction_data"]["qr_code"],
                "qr_code_base64": pagamento["point_of_interaction"]["transaction_data"]["qr_code_base64"]
            })
        else:
            # LOG detalhado para Render
            print(f"--- ERRO MERCADO PAGO ---")
            print(f"Status Code: {resultado.get('status')}")
            print(f"Resposta JSON: {pagamento}")
            print(f"-------------------------")
            
            mensagem_erro = pagamento.get('message', 'Erro desconhecido na API Mercado Pago')
            if "cause" in pagamento and pagamento["cause"]:
                detalhes = pagamento["cause"][0].get('description', '')
                mensagem_erro = f"{mensagem_erro}: {detalhes}"
            
            return jsonify({"sucesso": False, "mensagem": mensagem_erro})
            
    except Exception as e:
        import traceback
        print(f"EXCEPTION MP: {str(e)}")
        traceback.print_exc()
        return jsonify({"sucesso": False, "mensagem": f"Erro interno: {str(e)}"})

@app.route('/api/check_payment/<int:payment_id>', methods=['GET'])
def check_payment(payment_id):
    try:
        resultado = sdk.payment().get(payment_id)
        pagamento = resultado["response"]
        
        if pagamento.get("status") == "approved":
            partes = pagamento["external_reference"].split("_")
            user_id = int(partes[0])
            dias = int(partes[1])
            email_user = partes[2]
            
            nova_key = banco_dados.gerar_key_compra(user_id, dias, payment_id)
            
            if email_user and email_user != "cliente@email.com":
                corpo = f"<h2>Pagamento Aprovado! 🚀</h2><p>Sua Key de 16 dígitos é:</p><h3>{nova_key}</h3>"
                enviar_email(email_user, "Sua Key VIP - BS Optimizer Pro", corpo)
            
            return jsonify({"sucesso": True, "status": "approved", "key": nova_key})
            
        return jsonify({"sucesso": True, "status": pagamento.get("status", "pending")})
    except Exception as e:
        return jsonify({"sucesso": False, "mensagem": str(e)})

@app.route('/api/webhooks/mercadopago', methods=['POST'])
def webhook_mercadopago():
    try:
        # Pega os dados da notificação (MP envia via params ou body dependendo da versão)
        data = request.args if request.args else request.json
        print(f"WEBHOOK RECEBIDO: {data}")

        # O MP envia o ID do recurso e o tipo (ex: payment)
        id_recurso = data.get('data.id') or data.get('id')
        tipo = data.get('type') or data.get('topic')

        if tipo == 'payment' and id_recurso:
            # Consulta o status real do pagamento na API do MP
            resultado = sdk.payment().get(id_recurso)
            pagamento = resultado["response"]
            
            if pagamento.get("status") == "approved":
                ext_ref = pagamento.get("external_reference")
                if ext_ref:
                    partes = ext_ref.split("_")
                    user_id = int(partes[0])
                    dias = int(partes[1])
                    email_user = partes[2]
                    
                    # Gera a key (a função do banco já evita duplicatas pelo mp_id)
                    nova_key = banco_dados.gerar_key_compra(user_id, dias, id_recurso)
                    
                    if email_user and email_user != "cliente@email.com":
                        corpo = f"<h2>Pagamento Aprovado! 🚀</h2><p>Sua Key de 16 dígitos é:</p><h3>{nova_key}</h3>"
                        enviar_email(email_user, "Sua Key VIP - BS Optimizer Pro", corpo)
                    
                    print(f"WEBHOOK: Pagamento {id_recurso} APROVADO e Key Gerada.")
        
        return "OK", 200
    except Exception as e:
        print(f"ERRO WEBHOOK: {e}")
        return "Erro Interno", 500

@app.route('/api/desktop/login', methods=['POST'])
def desktop_login():
    dados = request.json
    usuario = dados.get('username')
    senha = dados.get('password')
    hwid = dados.get('hwid')
    if not usuario or not senha:
        return jsonify({"sucesso": False, "mensagem": "Usuário e senha são obrigatórios."})
    
    sucesso, user_id, msg = banco_dados.validar_login(usuario, senha, hwid)
    return jsonify({"sucesso": sucesso, "user_id": user_id, "mensagem": msg})

@app.route('/api/desktop/licenca', methods=['POST'])
def desktop_licenca():
    user_id = request.json.get('user_id')
    if not user_id:
        return jsonify({"sucesso": False, "mensagem": "ID de usuário ausente."})
    
    tem_licenca, dias_restantes = banco_dados.verificar_licenca_ativa(user_id)
    return jsonify({"sucesso": True, "tem_licenca": tem_licenca, "dias_restantes": dias_restantes})

@app.route('/api/desktop/ativar', methods=['POST'])
def desktop_ativar():
    dados = request.json
    user_id = dados.get('user_id')
    chave = dados.get('key')
    if not user_id or not chave:
        return jsonify({"sucesso": False, "mensagem": "ID de usuário e Key são obrigatórios."})
    
    sucesso, msg = banco_dados.ativar_key(user_id, chave)
    return jsonify({"sucesso": sucesso, "mensagem": msg})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    print(f"⚡ Servidor Web BS Optimizer rodando na porta {port}...")
    app.run(host='0.0.0.0', port=port)
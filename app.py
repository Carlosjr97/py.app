from flask import Flask, request
import requests
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

app = Flask(__name__)

ACCESS_TOKEN = "APP_USR-5902088609099212-031207-8a352c400797c6476bfb41e26c1d04c8-214625448"  # Pegue no painel do Mercado Pago

def verificar_pagamento(payment_id):
    """Consulta o status do pagamento no Mercado Pago"""
    url = f"https://api.mercadopago.com/v1/payments/{payment_id}"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    response = requests.get(url, headers=headers)
    return response.json()

def enviar_email(email_cliente):
    """Envia um e-mail com a planilha anexada"""
    remetente = "seuemail@gmail.com"
    senha = "suasenha"

    msg = MIMEMultipart()
    msg["From"] = remetente
    msg["To"] = email_cliente
    msg["Subject"] = "Seu Treino - Planilha de Emagrecimento"

    with open("minhajornadamaisleve.xlsx", "rb") as anexo:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(anexo.read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", "attachment; filename=planilha_treino.xlsx")
        msg.attach(part)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(remetente, senha)
        server.sendmail(remetente, email_cliente, msg.as_string())

    print("E-mail enviado!")

@app.route('/webhook', methods=['POST'])
def webhook():
    """Recebe notificações do Mercado Pago"""
    data = request.json
    if data.get("action") == "payment.updated":
        payment_id = data["data"]["id"]
        pagamento = verificar_pagamento(payment_id)
        
        if pagamento.get("status") == "approved":
            email_cliente = pagamento["payer"]["email"]
            enviar_email(email_cliente)

    return "OK", 200

if __name__ == '__main__':
    app.run(port=5000)

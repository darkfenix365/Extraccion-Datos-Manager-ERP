# Librerias a ocupar

import requests as rq
import json
import ast
from params import DB_MANAGER, DB_MANAGER_PASS
import pandas as pd

def manager_auth(manager_user, manager_pass):
    url = "https://lemontech.managermas.cl/api/auth/"

    payload = json.dumps({
    "username": manager_user,
    "password": manager_pass
    })
    headers = {
  'Content-Type': 'application/json'
    }
    respuesta_token = rq.request("POST", url, headers=headers, data=payload)

    token_manager = ast.literal_eval(respuesta_token.text)
    token_auth = token_manager['auth_token']
    return token_auth

def clientes_manager(token_manager_auth, rut_empresa):
  url = f"https://lemontech.managermas.cl/api/clients/{rut_empresa}/?contacts=1&direcciones=1"

  payload={}
  headers = {
    'Authorization': f'Token {token_manager_auth}',
    'Content-Type': 'application/json'
  }
  response = rq.request("GET", url, headers=headers, data=payload)
  respuesta = json.loads(response.text)
  respuesta_cliente_item = ast.literal_eval(json.dumps(respuesta, ensure_ascii=False).encode('utf8'))
  return respuesta_cliente_item
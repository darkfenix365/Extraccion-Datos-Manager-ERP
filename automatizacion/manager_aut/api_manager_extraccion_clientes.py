# Librerias a coupar
import requests as rq
import json
import ast
from params import DB_MANAGER, DB_MANAGER_PASS, DB_MANAGER_RUT
from funciones_manager import manager_auth

# LLamar funcion de archivo de autentificacion manager
token_manager = manager_auth(DB_MANAGER, DB_MANAGER_PASS)

# LLamar para extraer clientes de Manager
url = f"https://lemontech.managermas.cl/api/clients/{DB_MANAGER_RUT}/?contacts=1&direcciones=1"
payload={}
headers = {
  'Authorization': f'Token {token_manager}',
  'Content-Type': 'application/json'
}
response = rq.request("GET", url, headers=headers, data=payload)
respuesta = json.loads(response.text)
response_item = ast.literal_eval(json.dumps(respuesta, ensure_ascii=False).encode('utf8'))
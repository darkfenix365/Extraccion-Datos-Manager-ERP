# Librerias a ocupar

import requests as rq
import json
from params import DB_MANAGER, DB_MANAGER_PASS

# Url de api
url = "https://lemontech.managermas.cl/api/auth/"

payload = json.dumps({
  "username": DB_MANAGER,
  "password": DB_MANAGER_PASS
})
headers = {
  'Content-Type': 'application/json'
}
respuesta_token = rq.request("POST", url, headers=headers, data=payload)

print(respuesta_token.text)
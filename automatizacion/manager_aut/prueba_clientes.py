# Librerias a coupar
import requests as rq
import json
import ast
import pandas as pd
import numpy as np
from params import DB_MANAGER, DB_MANAGER_PASS, DB_MANAGER_RUT
from funciones_manager import manager_auth, clientes_manager

token = manager_auth(DB_MANAGER, DB_MANAGER_PASS)
clientes_manager_desc = clientes_manager(token, DB_MANAGER_RUT)

print(type(clientes_manager_desc))
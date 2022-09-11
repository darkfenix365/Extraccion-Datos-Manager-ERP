#Script para descargar informe de Tesoreria de ERP MANAGER a traves de Selenium

# Librerias a ocupar
from sqlite3 import Cursor
import tempfile
from time import sleep
from selenium import webdriver
from datetime import timedelta, date, datetime
from webdriver_manager.chrome import ChromeDriverManager
from params import DB_HOST, DB_PASSWORD, DB_MANAGER, DB_MANAGER_PASS, DB_PORT

# Generacion de fecha automatica formato DD-MM-YYYY
date_required = date.today() + timedelta(days= -1)
fecha_fin_descarga = date_required.strftime("%d/%m/%Y")

# Ingreso de Fecha de informe tesoreria
fecha_desde = '01/03/2000'
fecha_final = fecha_fin_descarga

# Generacion de carpeta temporal
temp = tempfile.TemporaryDirectory("w+t")
tempdir = temp.name

#Generacion de funcion de descarga en carpeta temporal

def create_driver():    
    # Chrome options
    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    download_argument = f'download.default_directory={tempdir}'
    print(download_argument)
    prefs = {'download.default_directory': f'{tempdir}'}
    options.add_experimental_option('prefs', prefs)
    # Conexccion a chrome driver
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    driver.maximize_window()
    driver.get('https://lemontech.managermas.cl/login/?next=/')
    return driver

driver = create_driver()

# Ingreso de usuarios y claves de manager
sleep(5)
driver.find_element("xpath", '/html[1]/body[1]/div[1]/div[1]/div[1]/form[1]/div[1]/div[1]/div[2]/div[1]/div[2]/div[1]/div[1]/input[1]').send_keys(DB_MANAGER)
driver.find_element("xpath",'/html[1]/body[1]/div[1]/div[1]/div[1]/form[1]/div[1]/div[1]/div[3]/div[1]/div[2]/div[1]/div[1]/input[1]').send_keys(DB_MANAGER_PASS)
driver.find_element("xpath",'/html[1]/body[1]/div[1]/div[1]/div[1]/form[1]/div[1]/div[1]/div[5]/div[1]/button[1]').click()
sleep(5)

# Ingreso a link de cuentas correientes en tesoreria
driver.get('https://lemontech.managermas.cl/reporting/T/INF/informe_cuenta_corriente/')
driver.find_element("xpath","//input[@id='id_desde']").clear()
driver.find_element("xpath","//input[@id='id_desde']").send_keys(fecha_desde)
driver.find_element("xpath","//input[@id='id_hasta']").clear()
driver.find_element("xpath","//input[@id='id_hasta']").send_keys(fecha_final)
sleep(5)

driver.find_element("xpath",'//*[@id="frm_generar_grilla_cuenta_corriente"]/div[5]/div[4]/label').click()
driver.find_element("xpath",'//*[@id="frm_generar_grilla_cuenta_corriente"]/div[5]/div[5]/label').click()

#Descargar excel de cobranza
driver.find_element("xpath","//i[@class='far fa-file-excel verde-excel']").click()
sleep(20)
driver.close()

#Librerias a ocupar para la data
import os
import pandas as pd
import numpy as np

 
xls_dir = tempdir
cont_xls = os.listdir(xls_dir)
xls_list = []

for xls_arch in cont_xls:
    if xls_arch.endswith('.xls'):
        xls_list.append(xls_dir + '/' + xls_arch)

# Lectura de Excel Informe Tesoreria y eliminacion de columnas
df = pd.read_excel(xls_list[0], skipfooter= 1)
df.drop(['Clasificación', 'Vendedor', 'Cobrador', 'U. Negocio', 'C.C.', 'EmailSii', 'Email'], axis=1, inplace = True)
df_filtrado = df.iloc[:, :15]

# Creacion columna de Categoria Documento; Factura, Nota de Credito, Nota de Debito, Anticipo
df_filtrado['Cat_Documento']=(np.where(((df_filtrado['Documento'] == 'FAVE')|(df_filtrado['Documento'] == 'FEXE')|(df_filtrado['Documento'] == 'FVEE')|(df_filtrado['Documento'] == 'FEX')) ,'Factura',
                              np.where(((df_filtrado['Documento'] == 'NCEX')|(df_filtrado['Documento'] == 'NCEXE')|(df_filtrado['Documento'] == 'NCV')|(df_filtrado['Documento'] == 'NCVE')) ,'Nota de Credito',
                              np.where(((df_filtrado['Documento'] == 'ANDCL')|(df_filtrado['Documento'] == 'ANTCL')|(df_filtrado['Documento'] == 'ASCEX')) ,'Anticipo', 
                              np.where(((df_filtrado['Documento'] == 'NDEXE')|(df_filtrado['Documento'] == 'NDVE')), 'Nota de Debito', 'Sin categoria'
                              )))))

# Creacion columna de Tipo de cuenta; Nacional e Internacional
df_filtrado['Tipo_Cuenta'] = (np.where(((df_filtrado['CuentaContable'] == 110501)|(df_filtrado['CuentaContable'] == 210309)),'Nacional',
                              np.where(((df_filtrado['CuentaContable'] == 110502)|(df_filtrado['CuentaContable'] == 210310)),'Internacional', 'Sin Categoria')))

# Creacion de columnas de Fechas 
df_filtrado['Fecha_Tr'] = fecha_final
mes = input('Ingrese mes de descarga: ')
df_filtrado['Mes'] = mes
df_filtrado['Año'] = df_filtrado['Fecha_Tr'].str[-4:]
df_filtrado['Año'] = pd.to_numeric(df_filtrado['Año'])

#Isnertar Data BD Nube

import psycopg2 as psy2
import pandas as pd

db = psy2.connect(host = DB_HOST,
                 user ='postgres',
                 password = DB_PASSWORD,
                 database = "adm_finanzas")

db.autocommit = True

cursor1 = db.cursor()

for index, row in df_filtrado.iterrows():
    data = []
    data.append(row)
    for d in data:
        cursor1.execute('INSERT INTO  public.cobranza_cxc_lemonspa("CuentaContable", "Rut", "ClienteProveedor", "NombreFantasia", "Documento", "NumDocumento", "FechaEmision", "FechaVencimiento", "Debe", "Haber", "Saldo", "Moneda", "Tasa_Cambio", "Total", "Deuda", "Cat_Documento", "Tipo_Cuenta", "Fecha_Tr", "Mes", "Año") VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)', d)
        db.commit()

cursor1.close()
db.close()
temp.cleanup()


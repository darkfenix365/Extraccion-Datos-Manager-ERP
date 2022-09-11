#Script para descargar informe de libro de Venta de ERP MANAGER a traves de Selenium

# Librerias a ocupar
from sqlite3 import Cursor
from time import sleep
from selenium import webdriver
import tempfile
from webdriver_manager.chrome import ChromeDriverManager
from params import DB_HOST, DB_PASSWORD, DB_MANAGER, DB_MANAGER_PASS, DB_PORT                           


# Ingreso de Fecha de  Balance formato DD/MM/YYYY
fecha_desde = input('Ingrese fecha a descargar inicio de estado de cuenta: ')
fecha_final = input('Ingrese fecha a descargar fin de estado de cuenta: ')


temp = tempfile.TemporaryDirectory("w+t")
tempdir = temp.name
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
driver.find_element("xpath", '/html[1]/body[1]/div[1]/div[1]/div[1]/form[1]/div[1]/div[1]/div[3]/div[1]/div[2]/div[1]/div[1]/input[1]').send_keys(DB_MANAGER_PASS)
driver.find_element("xpath", '/html[1]/body[1]/div[1]/div[1]/div[1]/form[1]/div[1]/div[1]/div[5]/div[1]/button[1]').click()
sleep(10)

# Ingresar a Finanzas -> Informes Tributarios -> Libro de ventas
driver.find_element("xpath", '/html[1]/body[1]/div[1]/div[1]/div[1]/div[1]/div[1]/ul[2]/div[5]/div[1]/div[2]/p[1]').click()
sleep(3)
driver.find_element("xpath", '/html[1]/body[1]/div[1]/div[1]/div[1]/div[1]/div[1]/ul[2]/div[5]/div[2]/div[1]/div[1]/div[1]/div[2]/div[1]/p[1]').click()
sleep(3)
driver.get('https://lemontech.managermas.cl/reporting/FIN/LIB/libro_venta/')

#Ingresar Fecha de inicio y fecha Fin en Informe de Ventas
driver.find_element("xpath", "//input[@id='id_desde']").clear()
driver.find_element("xpath", "//input[@id='id_desde']").send_keys(fecha_desde)
driver.find_element("xpath", "//input[@id='id_hasta']").clear()
driver.find_element("xpath", "//input[@id='id_hasta']").send_keys(fecha_final)
sleep(5)

# Desccargar Libro de Ventas
driver.find_element("xpath", "//i[@class='far fa-file-excel verde-excel']").click()
sleep(20)
driver.close()

# Librerias a ocupar
import os
import pandas as pd
import numpy as np

# Importar a dataframe archivo
xls_dir = tempdir

cont_xls = os.listdir(xls_dir)

xls_list = []

for xls_arch in cont_xls:
    if xls_arch.endswith('.xls'):
        xls_list.append(xls_dir + '/' + xls_arch)

#lectura de archivo
df = pd.read_excel(xls_list[0], skipfooter= 1)
df.drop(['Código doc. ', 'Documento', 'Cliente', 'Empresa','Afecto', 'Exento', 'Neto', 'Iva'], axis=1, inplace = True)
df = df[['Fecha', 'Num doc','Rut', 'Razón social' ,'Tipo doc', 'Total']]
df_filtrado = df

# generacion col. Tipo Documento

df_filtrado['Cat_Documento']=(np.where(((df_filtrado['Tipo doc'] == 'FAVE')|(df_filtrado['Tipo doc'] == 'FEXE')|(df_filtrado['Tipo doc'] == 'FVEE')|(df_filtrado['Tipo doc'] == 'FEX')|(df_filtrado['Tipo doc'] == 'FAV')|(df_filtrado['Tipo doc'] == 'FAVI')) ,'Factura',
                              np.where(((df_filtrado['Tipo doc'] == 'NCEX')|(df_filtrado['Tipo doc'] == 'NCEXE')|(df_filtrado['Tipo doc'] == 'NCV')|(df_filtrado['Tipo doc'] == 'NCVE')) ,'Nota de Credito',
                              np.where(((df_filtrado['Tipo doc'] == 'ANDCL')|(df_filtrado['Tipo doc'] == 'ANTCL')|(df_filtrado['Tipo doc'] == 'ASCEX')) ,'Anticipo', 
                              np.where(((df_filtrado['Tipo doc'] == 'NDEXE')|(df_filtrado['Tipo doc'] == 'NDVE')), 'Nota de Debito', 'Sin categoria'
                              )))))

#Generacion col.Cartera
df_filtrado['Cartera'] =  (np.where(((df_filtrado['Tipo doc'] == 'FAV')|(df_filtrado['Tipo doc'] == 'FAVE')|(df_filtrado['Tipo doc'] == 'FAVI')|(df_filtrado['Tipo doc'] == 'FVEE')|(df_filtrado['Tipo doc'] == 'NCV')|(df_filtrado['Tipo doc'] == 'NCVE')|(df_filtrado['Tipo doc'] == 'NDVE')),'Nacional',
                           np.where(((df_filtrado['Tipo doc'] == 'FEX')|(df_filtrado['Tipo doc'] == 'FEXE')|(df_filtrado['Tipo doc'] == 'NCEX')|(df_filtrado['Tipo doc'] == 'NCEXE')|(df_filtrado['Tipo doc'] == 'NDEXE')),'Internacional', 'Sin Categoria')))


df_filtrado['Fecha_Tr'] = fecha_final

#Carga de datos en base de datos
import psycopg2 
from sqlalchemy import create_engine

conn = psycopg2.connect(
    database = 'adm_finanzas', user = 'postgres', password = DB_PASSWORD, host = DB_HOST, port = DB_PORT
)
conn.autocommit = True

cursor = conn.cursor()

for index, row in df_filtrado.iterrows():
    data = []
    data.append(row)
    for d in data:
        cursor.execute('INSERT INTO public.cobranza_dso_semanal_fact_lemonspa("Fecha", "Num doc", "Rut", "Razón social", "Tipo doc", "Total", "Cat_Documento", "Cartera", "Fecha_Tr") VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)', d)
        conn.commit()

cursor.close()
conn.close()
temp.cleanup()

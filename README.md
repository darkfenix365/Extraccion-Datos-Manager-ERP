![This is an image](https://manager.cl/wp-content/uploads/2022/02/logo-manager-mas.png)
# Manager-Automatizacion 

## Objetivo 
El presente repositorio tiene como finalidad el uso de Scripts de python para la descarga de distintos informes del ERP MANAGER y consumo de API de MANAGER.

### Explicación Scripts
Los ditintos Scripts tienen la caracteristicas de Estructurarse como ETL de descarga de informes en formato xlsx, para luego transformar a traves de pandas y luego su carga en una base de datos.

#### Librerias a Ocupar
- Selenium
- webdriver_manager
- tempfile
- pandas
- numpy
- psycop2
- sqlalchemy

## Informes de MANAGER
- **Informe de Tesoreria**: Informe Manager de Cuentas Por Cobrar pendientes.
- **Informe de Libro de Venta**: Informe Manager de libro de documentos emitido por compañia.

## Codigo de Api manager
- **Api Autentificador**: Consumir api para obtener token de autentificacion.
- **Api Descargar Clientes** : Consumir api para descargar datos de clientes de empresa.

## Puntos a Mejorar
 - [ ] **Mejorar funciones para generar dataframe de valores**

## Documentacion
La documentación de la api de Manager la pueden encontrar en el siguiente vinculo [Manager Documentacion](https://api.managermas.cl/).

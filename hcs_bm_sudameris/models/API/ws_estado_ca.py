from datetime import datetime
import requests
import json
import logging

_logger = logging.getLogger(__name__)


class ApiWsEstadoCuenta:
  def __init__(self, base_url, authenticate):
    self.base_url = base_url
    self.authenticate = authenticate

  """
  Servicio: Estado de la Caja de Ahorro
  Metodo: POST
  URL: https://10.100.14.2:9280/bantotal/servlet/com.dlya.bantotal.odwsbt_BSPayroll?WSEstadoCA
  """
  def ws_estado_ca(self, account_number, module, currency_code, *args, **kwargs):
    """ Parametros
    Btinreq:    Credenciales        |   Object
    Cuenta:     Número de cuenta    |   N(9)
    Sucursal:   Número de sucursal  |   N(3)    | Si no se envía, se busca la Caja de Ahorro por Modulo y moneda
    Modulo:     Módulo(?)           |   N(3)
    Moneda:     Código de moneda    |   N(4)

    # RESPONSE
    Cuenta:         Número de cuenta    |   N(9)
    Sucursal:       Número de sucursal  |   N(3)
    Modulo:         Módulo(?)           |   N(3)
    Moneda:         Código de moneda    |   N(4)
    Estado:         Estado de la Cuenta |   N(2)
    CodRetorno:     Código de Retorno   |   N(2)
    Mensaje:        Nombre de Persona   |   C(100)  | Puede existir varias CA para una cuenta en sucursales distintas.
    """
    wsurl = self.base_url + "WSEstadoCA"
    headers = {'Content-Type': 'application/json'} # set what your server accepts
    request_body = json.dumps({
        "Btinreq": self.authenticate['Btinreq'],
        "Parametros": {
          "Parametro": {
            "sBTRepParametros.It": [{
              "Tipo": "Texto",
              "Nombre": "CUENTA",
              "Codigo": 5,
              "Valor": account_number
            }, {
              "Tipo": "Entero",
              "Nombre": "MODULO",
              "Codigo": 6,
              "Valor": module
            }, {
              "Tipo": "Entero",
              "Nombre": "MONEDA",
              "Codigo": 7,
              "Valor": currency_code
            }]
          }
        }
      })
    try:
      response = requests.post(wsurl, data=request_body, headers=headers, verify=False, timeout=10)
      _logger.debug(['APIRESPONSE', response.text])
      response = json.loads(response.text)
      return {
          "cuenta": '',
          "sucursal": '',
          "modulo": '',
          "moneda": '',
          "estado": '',
          "codretorno": '',
          "mensaje": ''
      }
    except:
      return {
          "cuenta": None,
          "sucursal": None,
          "modulo": None,
          "moneda": None,
          "estado": None,
          "codretorno": None,
          "mensaje": None
      }

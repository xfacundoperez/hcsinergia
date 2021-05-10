from datetime import datetime
import requests
import json
import logging
import random

_logger = logging.getLogger(__name__)

"""
    API Exclusiva para Sudameris Bank
"""
class BM_ApiBase:
    # Variables de la clase

    def __init__(self, config_parameter):
        self.config_parameter = config_parameter
        self.base_url = "http://10.100.14.2:9280/bantotal/servlet/com.dlya.bantotal.odwsbt_BSPAYROOL?"
        self.authenticate = {
            "Btinreq": {
                "Device": "10.103.103.31",
                "Usuario": "GEIER",
                "Requerimiento": "1",
                "Canal": "BTINTERNO",
                "Token": None
            },
            "userID": "GEIER",
            "userPassword": "Albuquerque2021"
        }

    def ws_authenticate(self):
        from .ws_authenticate_api import ApiWsAuthenticate
        _api = ApiWsAuthenticate(self.base_url, self.authenticate, self.config_parameter)
        token = _api.get_token()
        self.authenticate['Btinreq']['Token'] = token

    def ws_valid_client_reliable_base(self, Pais, Tdoc, Ndoc, Nomb1, Nomb2, Apell1, Apell2, FecNac):
        # update token
        self.ws_authenticate()     
        # random result
        for _ in range(2):
            r = bool(random.randint(0, 1))
        result = {
            'state': r,
        }
        return result
        # get validation data
        #from .ws_valida_base_confiable import ApiWsValidaBaseConfiable
        #_api = ApiWsValidaBaseConfiable(self.base_url, self.authenticate)
        #return _api.ws_valida_base_confiable(Pais, Tdoc, Ndoc, Nomb1, Nomb2, Apell1, Apell2, FecNac)


    def ws_client_owns_account(self, Pais, Tdoc, Ndoc, *args, **kwargs):
        # update token
        self.ws_authenticate()     
        # random result
        for _ in range(2):
            r = bool(random.randint(0, 1))
        result = {
            'state': r,
            'account_number': random.randint(1704048, 3917590),
            'account_name': random.choice(['CANCELADO', 'INACTIVO', 'NORMAL', 'PACON']),
            'branch_number': random.choice([10, 24, 25])
        }
        return result
        #from .ws_cliente_posee_cuenta import ApiWsClientePoseeCuenta
        #_api = ApiWsClientePoseeCuenta(self.base_url, self.authenticate)
        #return _api.ws_cliente_posee_cuenta(Pais, Tdoc, Ndoc)
        
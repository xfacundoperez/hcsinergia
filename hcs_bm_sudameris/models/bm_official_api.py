from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from .API.ws_base_api import BM_ApiBase

import logging
_logger = logging.getLogger(__name__)


class BM_OfficialApi(models.Model):
    _inherit = "bm.official"

    def valid_client_reliable_base(self, official_id=None):
        # Creo la clase y le paso como parametro ir.config_parameter como sudo
        _bm_api = BM_ApiBase(self.env['ir.config_parameter'].sudo())
        if official_id:
            officials = self.env['bm.official'].search([('id', '=', official_id)])
        else:
            officials = self.env['bm.official'].search([('id', 'in', self.env.context.get('active_ids'))])
        for official in officials:
            # Solo consulto si no fue verificado
            if not official.reliable_base:
                # Hago la consulta a la API
                _api_response = _bm_api.ws_valid_client_reliable_base(
                    official.country.code_number,
                    official.identification_type,
                    official.identification_id,
                    official.name_first,
                    official.name_second,
                    official.surname_first,
                    official.surname_second,
                    official.birthday
                )
                if _api_response:
                    official.reliable_base = (_api_response['Mensaje'] == 'La Persona Existe')
            # Obtengo el numero de cuenta
            self.client_owns_account(_bm_api, official.id)
        
    def client_owns_account(self, _bm_api, official_id):
        for official in self.env['bm.official'].search([('id', '=', official_id)]):
            if not (official.account_number and official.account_name and official.branch_number): 
                # Hago la consulta a la API
                _api_response = _bm_api.ws_client_owns_account(
                    official.country.code_number,
                    official.identification_type,
                    official.identification_id,
                )
                # Si obtengo el numero de cuenta, por ende obtengo el nombre de la cuenta y el numero de la sucursal
                if _api_response:
                    if _api_response['account_number']:
                        official.account_number = _api_response['account_number']
                        official.account_name = _api_response['account_name']
                        official.branch_number = _api_response['branch_number']
                    else:
                        official.account_number = None
                        official.account_name = None
                        official.branch_number = None

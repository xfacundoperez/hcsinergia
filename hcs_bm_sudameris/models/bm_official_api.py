from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from .API.ws_base_api import BM_ApiBase

#import logging
#_logger = logging.getLogger(__name__)


class BM_OfficialApi(models.Model):
    _inherit = "bm.official"

    def valid_client_reliable_base(self, *args):
        # Checkeo que el usuario actual tiene el permiso del banco
        if not self.env.user.has_group('hcs_bm_sudameris.group_bm_bank') and not args:
            return self.show_message('Validar', 'Usted no tiene permiso para ejecutar esta accion')

        # Get officials in check and not reliable_base or ready, error and not reliable_base
        _search = ['&', ('state', 'in', ['check', 'ready', 'error']), ('reliable_base', '=', False)]
        
        # If are active_ids, search it only
        active_ids = self._context.get('active_ids')
        if active_ids:
            _search = ['&', '&', ('id', 'in', active_ids), ('state', 'in', ['check', 'ready', 'error']), ('reliable_base', '=', False)]

        func_result = {
            'validations': {
                'error': [],
                'message': ''
            },
            'count_ok': 0
        }
        # Creo la clase y le paso como parametro ir.config_parameter como sudo
        _bm_api = BM_ApiBase(self.env['ir.config_parameter'].sudo())
        
        for official in self.env['bm.official'].search(_search):
            # Hago la consulta a la API
            _api_response = _bm_api.ws_valid_client_reliable_base(
                official.country.name,
                official.identification_type,
                official.identification_id,
                official.name_first,
                official.surname_second,
                official.name_first,
                official.surname_second,
                official.birthday
            )
            official.reliable_base = _api_response['state']
            if official.reliable_base:
                official.state = 'ready' 
                func_result['count_ok'] += 1
            else:
                func_result['validations']['error'].append('{} ({})'.format(official.name, official.identification_id))

        if len(func_result['validations']['error']) > 0:
            func_result['validations']['message'] = '\nLos siguientes funcionarios no pudieron ser validados:\n\n{}'.format('\n'.join(func_result['validations']['error']))
        if not args:
            return self.show_message('Validar', 'Se validaron {} funcionarios.\n{}'.format(func_result['count_ok'], func_result['validations']['message']))

    def client_owns_account(self, *args):
        # Checkeo que el usuario actual tiene el permiso del banco
        if not self.env.user.has_group('hcs_bm.group_bm_bank') and not args:
            return self.show_message('Validar', 'Usted no tiene permiso para ejecutar esta accion')

        # Get officials in check and not reliable_base or ready, error and not reliable_base
        _search = ['&', '&', ('state', 'in', ['check', 'ready', 'error']), ('reliable_base', '=', True), ('account_number', '=', None)]
        
        # If are active_ids, search it only
        active_ids = self._context.get('active_ids')
        if active_ids:
            _search = ['&', '&', ('id', 'in', active_ids), ('state', 'in', ['check', 'ready', 'error']), '&', ('reliable_base', '=', True), ('account_number', '=', None)]

        func_result = {
            'validations': {
                'error': [],
                'message': ''
            },
            'count_ok': 0
        }
        # Creo la clase y le paso como parametro ir.config_parameter como sudo
        _bm_api = BM_ApiBase(self.env['ir.config_parameter'].sudo())

        for official in self.env['bm.official'].search(_search):
            # Hago la consulta a la API
            _api_response = _bm_api.ws_client_owns_account(
                official.country.name,
                official.identification_type,
                official.identification_id
            )
            if _api_response['state']:
                official.account_number = _api_response['account_number']
                official.account_name = _api_response['account_name']
                official.branch_number = _api_response['branch_number']
                func_result['count_ok'] += 1
            else:
                func_result['validations']['error'].append('{} ({})'.format(official.name, official.identification_id))

        if len(func_result['validations']['error']) > 0:
            func_result['validations']['message'] = '\nLos siguientes funcionarios no poseen cuenta:\n\n{}'.format('\n'.join(func_result['validations']['error']))
        if not args:
            return self.show_message('Verificar cuenta', 'Se verificó la cuenta de {} funcionarios.\n{}'.format(func_result['count_ok'], func_result['validations']['message']))
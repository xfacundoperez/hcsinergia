from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from random import randint

#import logging
#_logger = logging.getLogger(__name__)


class BM_OfficialApi(models.Model):
    _inherit = "bm.official"

    def valid_client_reliable_base(self, *args):
        # Checkeo que el usuario actual tiene el permiso del banco
        if not self.env.user.has_group('hcs_bm_sudameris.group_bm_bank') and not args:
            return self.show_message('Validar', 'Usted no tiene permiso para ejecutar esta opción')

        # Get officials in check and not reliable_base or ready, error and not reliable_base
        _search = ['&', ('state', 'in', ['check', 'ready', 'error']), ('reliable_base', '=', False)]
        
        # If are active_ids, search it only
        active_ids = self._context.get('active_ids')
        if active_ids:
            _search = ['&', '&', ('id', 'in', active_ids), ('state', 'in', ['check', 'ready', 'error']), ('reliable_base', '=', False)]

        _changes = []
        _ready_count = 0
        for official in self.env['bm.official'].search(_search):
            for _ in range(2):
                official.reliable_base = bool(randint(0, 1))
            if official.reliable_base:
                official.state = 'ready' 
                _ready_count += 1
            else:
                _changes.append('{} No se pudo validar su identidad'.format(official.name))
        if _ready_count > 1:
            _changes.append('Se validaron {} funcionarios'.format(_ready_count))
        if len(_changes) and not args:
            return self.show_message('Validar', '\n'.join(_changes))

    def client_owns_account(self):
        # Checkeo que el usuario actual
        if not self.env.user.company_id.id == 1:
            return self.show_message('Cliente posee cuenta', 'Cuando todo esté listo, un representante del banco Sudameris podrá verificar el estado del funcionario.')
        _changes = []
        # Creo la clase y le paso como parametro ir.config_parameter como sudo
        _config_parameter = self.env['ir.config_parameter'].sudo()
        sudamerisApi = SudamerisApiBase(_config_parameter)
        # Obtengo los funcionarios seleccionados y verifco cada uno
        for funcionario in self.env['bm.official'].browse(self._context.get('active_ids')):
            if funcionario.state == 'borrador':
                _changes.append(
                    '{} todavia no está aprobado, debe estar En Proceso de Alta'.format(funcionario.name))
                continue
            if funcionario.state == 'listo' and funcionario.numero_cuenta != '':
                _changes.append(
                    '{} ya posee una cuenta en el banco'.format(funcionario.name))
                continue
            # Hago la consulta a la API
            result = sudamerisApi.ws_cliente_posee_cuenta(
                funcionario.country_id.name, funcionario.tipo_documento, funcionario.identification_id)
            for res in result:
                _valor = res["Filas"]["RepFilas.Fila"][0]["Valor"]
                if res['Descripcion'] == "CTNRO":  # Número de cuenta
                    funcionario.numero_cuenta = _valor
                if res['Descripcion'] == "Cttfir":  # Sucursal
                    funcionario.numero_sucursal = 1
                if res['Descripcion'] == "Observacion":  # Descripción de la cuenta
                    funcionario.nombre_cuenta = _valor
            # Guardo la respuestas correspondientes y marco el funcionario como listo
            funcionario.state = 'listo'
            _changes.append(
                '{} obtuvo su cuenta correctamente'.format(funcionario.name))
        return self.show_message('Cliente Posee Cuenta', '\n'.join(_changes))

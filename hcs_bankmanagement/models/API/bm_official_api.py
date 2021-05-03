from odoo import fields, models, api, _
#from odoo.exceptions import ValidationError

#import logging
#_logger = logging.getLogger(__name__)


class BM_OfficialApi(models.Model):
    _name = "bm.official.api"
    _inherit = "bm.official"

    def valid_client_reliable_base(self):
        return self.show_message('TEST OK')
        _changes = []
        # Creo la clase y le paso como parametro ir.config_parameter como sudo
        _config_parameter = self.env['ir.config_parameter'].sudo()
        sudamerisApi = SudamerisApiBase(_config_parameter)
        # Obtengo la lista de funcionarios seleccionados
        for official in self.env['bm.official'].browse(self._context.get('active_ids')) or self:
            # Hago la consulta a la API
            result = sudamerisApi.ws_valida_reliable_base(
                official.country_id.name,
                official.identification_type,
                official.identification_id,
                official.name_first,
                official.name_second,
                official.surname_first,
                official.surname_second,
                official.birthday
            )
            official.reliable_base = result[0]
            if result[0] == True:
                self.cliente_posee_cuenta()
            else:
                _changes.append('{}: {}'.format(official.name, result[1]))
        if len(_changes):
            return self.show_message('Cliente Valida Base Confiable: Se encontraron los siguientes errores', '\n'.join(_changes))

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

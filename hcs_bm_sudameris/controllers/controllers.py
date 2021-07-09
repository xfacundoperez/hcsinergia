# -*- coding: utf-8 -*-
from odoo import http
from datetime import datetime
import tempfile

#import logging
#_logger = logging.getLogger(__name__)

class BM_OfficialSalary_Controller(http.Controller):
    @http.route('/web/binary_text/create_file_txt', type='http', auth="user")
    def index(self, req):
        #Si no se pasaron ids, no genera nada
        if not req.params.get('ids'):
            return False
        _ids = req.params.get('ids')
        _fecha_pago = datetime.now().strftime("%d/%m/%Y")
        _referencia = '202005902952101999'

        # Get the selected official's salary movement
        officials_salary = http.request.env['bm.official.salary'].search([('id', 'in', _ids.split(','))])
        # Creo el TXT
        # Tipo de dato: I: Entero, C: Caracter o Alfanumérico, D: Fecha, N: Numérico decimal con dos valores decimales
        # Composición del nombre: ENTIDAD_SERVICIO_FECHA+HORA.TXT
        file_title = 'Pago_de_Salario_via_Banco_{}.txt'.format(datetime.now().strftime("%Y%m%d%H%M%S"))
        file_content_detail = ''
        _amount_to_pay_sum = 0
        for official_salary in officials_salary:
            _amount_to_pay_sum += official_salary.amount_to_pay
            file_content_detail += "{};{};{};{};{};{};{};{};{};{};{};{};{};{};{};{};{};{};{};{};{};{};{}\n".format(
                'D',                                                # Identificador del detalle(C:1)
                'Pago_de_Salario_via_Banco',                        # Concepto(C:30)
                official_salary.official.surname_first,             # Primer Apellido(C:15)
                official_salary.official.surname_second or '',      # Segundo Apellido(C:15)
                official_salary.official.name_first,                # Primer Nombre(C:15)
                official_salary.official.name_second or '',         # Segundo Nombre(C:15)
                official_salary.official.country.code_number,       # País(I:3)
                official_salary.official.identification_type,       # Tipo de Documento(I:2)
                official_salary.official.identification_id,         # Número de Documento(C:15)
                official_salary.official.currency_type,             # Moneda(I:4)
                official_salary.amount_to_pay,                      # Importe(N:15.2)
                official_salary.payment_date or '',                 # Fecha de Pago(D:8)
                official_salary.payment_mode or '',                 # Modalidad de Pago(I:3)
                official_salary.official.account_number or '',      # Número de Cuenta(I:9)
                official_salary.official.branch_number,             # Sucursal Empleado(I:3)
                official_salary.official.currency_type,             # Moneda Empleado(I:4)
                '0',                                                # Operación Empleado(I:9): En estos campos va siempre el numero 0
                '0',                                                # Tipo de Operación Empleado(I:3): En estos campos va siempre el numero 0
                '0',                                                # Suboperación Empleado(I:3): En estos campos va siempre el numero 0
                _referencia,                                        # Referencia(C:18): Dicho campo debe ser exactamente igual que el campo REFERENCIA en la CABECERA
                '1',                                                # Tipo de Contrato(I:3): Este campo se coloca siempre el numero 1
                official_salary.official.gross_salary or '0.00',    # Sueldo Bruto(N:15.2)
                official_salary.official.contract_end_date or '//', # Fecha Fin de Contrato(D:8)
            )

        file_content_header = '{};{};{};{};{};{};{};{};1;1;1982073;10;20;6900;0;0;0\n'.format(
            'H',                    # Identificador de cabecera(C:1)
            '999',                  # Código de contrato(I:9)
            'mail@entidad.com',     # E-mail asociado al Servicio(C:50)
            '6900',                 # Moneda(I:4)
            _amount_to_pay_sum,     # Importe(N:15.2)
            len(_ids),              # Cantidad de Documentos(I:5)
            _fecha_pago,            # Fecha de Pago(D:8)
            _referencia,            # Referencia(C:18)
            '1',                    # Tipo de Cobro(I:3)
            '1',                    # Debito Crédito(I:1)
            '1982073',              # Cuenta Débito(I:9)
            '10',                   # Sucursal Débito(I:3)
            '20',                   # Módulo Débito(I:3)
            '6900',                 # Moneda Débito(I:4)
            '0',                    # Operación Débito(I:9)
            '0',                    # Sub Operación Débito(I:3)
            '0'                     # Tipo Operación Débito(I:3)
            )


        file_content = str.encode(file_content_header + file_content_detail)
        # Create temporary file, write info and download
        tmp_file = tempfile.TemporaryFile()
        # Write data into your file respectively with your logic
        tmp_file.write(file_content)
        tmp_file.seek(0)
        file = tmp_file.read()
        tmp_file.close()
        
        return req.make_response(
            file, headers=[
                ('Content-Disposition', 'attachment; filename="{}"'.format(file_title)),
                ('Content-Type', 'text/plain')
            ])

# -*- coding: utf-8 -*-
from odoo import http
from datetime import datetime
import logging
import tempfile

_logger = logging.getLogger(__name__)

class Sudameris_employee_salary_movement_controller(http.Controller):
    @http.route('/web/binary_text/crear_txt', type='http', auth="user")
    def index(self, req):        
        # Composición del nombre: ENTIDAD_SERVICIO_FECHA+HORA.TXT
        # Ejemplo: GESTION_PAGODESALARIOS_20200519103252.TXT
        # Tipo de dato: I: Entero, C: Caracter o Alfanumérico, D: Fecha, N: Numérico decimal con dos valores decimales
        ## CABECERA: Identificador de cabecera(C:1);Código de contrato(I:9);E-mail asociado al Servicio(C:50);Moneda(I:4);Importe(N:15.2);Cantidad de Documentos(I:5); \
        ## Fecha de Pago(D:8);Referencia(C:18);Tipo de Cobro(I:3);Debito Crédito(I:1);Cuenta Débito(I:9);Sucursal Débito(I:3);Módulo Débito(I:3); \ 
        ## Moneda Débito(I:4)Operación Débito(I:9);Sub Operación Débito(I:3);Tipo Operación Débito(I:3)
        # Ejemplo CABECERA: H;999;mail@entidad.com;6900;52000.00;1;19/05/20; 202005902952101999;1;1;1982073;10;20;6900;0;0;0
        ## DETALLE: Identificador del detalle(C:1);Concepto(C:30);Primer Apellido(C:15);Segundo Apellido(C:15);Primer Nombre(C:15);Segundo Nombre(C:15); \ 
        ## País(I:3);Tipo de Documento(I:2);Número de Documento(C:15);Moneda(I:4);Importe(N:15.2);Fecha de Pago(D:8);Modalidad de Pago(I:3); \ 
        ## Número de Cuenta(I:9);Sucursal Empleado(I:3);Moneda Empleado(I:4);Operación Empleado(I:9);Tipo de Operación Empleado(I:3);Suboperación Empleado(I:3); \ 
        ## Referencia(C:18);Tipo de Contrato(I:3);Sueldo Bruto(N:15.2);Fecha Fin de Contrato(D:8);
        # Ejemplo DETALLE: D;PAGO DE SALARIO VIA BANCO;APELLIDO 1;APELLIDO 2;NOMBRE 1;NOMBRE 2;586;1;111222;6900;52000.00;19/05/20;21;498154;10;6900;0;0;0;202005902952101999;1;528000.00;31/12/99
        # _txt = 'Token: {}\n'.format(get_token)
        # Obtengo los movimientos seleccionados
        movimientos = http.request.env['sudameris_employee_salary_movement'].search([('id', 'in', req.params.get('ids').split(','))])
        # Creo el TXT
        _txt_title = 'SUDAMERIS_ODOO_{}.txt'.format(datetime.strftime(datetime.now(), '%Y%m%d%H%M%S'))
        _txt_content_header = 'H;999;mail@entidad.com;6900;52000.00;1;19/05/20;202005902952101999;1;1;1982073;10;20;6900;0;0;0\n'
        _txt_content_detail = ''
        for rec in movimientos:
            if rec.state == 'aprobado':
                empleado = rec.empleado
                # Obtengo los nombres
                _nombres = empleado.nombres.split(' ')
                # Si solo tiene 1 nombre, agrego un string vacio
                if len(_nombres) == 1:
                    _nombres.append('')
                # Obtengo los apellidos
                _apellidos = empleado.apellidos.split(' ')
                # Si solo tiene 1 apellido, agrego un string vacio
                if len(_apellidos) == 1:
                    _apellidos.append('')
                # Genero el detalle con los datos del empleado
                #D;PAGO DE SALARIO VIA BANCO;APELLIDO 1;APELLIDO 2;NOMBRE 1;NOMBRE 2;586;1;111222;6900;52000.00;19/05/20;21;498154;10;6900;0;0;0;202005902952101999;1;528000.00;31/12/99
                _detalle = "D;SUDAMERIS_ODOO;{0};{1};{2};{3};{4};{5};{6};{7};{8};{9};{10};{11};{12};{13};{14};{15};{16};{17};{18};{19};{20}\n".format(
                _apellidos[0], _apellidos[1], _nombres[0], _nombres[1],
                empleado.country_id.name, empleado.tipo_documento, empleado.identification_id,
                rec.moneda, rec.salario_importe, rec.fecha_pago, rec.modalidad_pago, empleado.numero_cuenta,
                empleado.numero_sucursal, empleado.tipo_moneda, rec.codigo_operacion, rec.tipo_operacion,
                rec.codigo_suboperacion, rec.referencia, empleado.tipo_contrato,
                empleado.salario_bruto, empleado.fecha_fin_contrato,
                )
                _txt_content_detail += _detalle       
        fp = tempfile.TemporaryFile()
        # Write data into your file respectively with your logic
        fp.write(str.encode(_txt_content_header + _txt_content_detail))
        fp.seek(0)
        file_data = fp.read()
        fp.close()
        return req.make_response(
            file_data, headers=[
                ('Content-Disposition', 'attachment; filename="{}"'.format(_txt_title)),
                ('Content-Type', 'text/plain')
            ])

    
#     @http.route('/hcs_sudameris/hcs_sudameris/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/hcs_sudameris/hcs_sudameris/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('hcs_sudameris.listing', {
#             'root': '/hcs_sudameris/hcs_sudameris',
#             'objects': http.request.env['hcs_sudameris.hcs_sudameris'].search([]),
#         })

#     @http.route('/hcs_sudameris/hcs_sudameris/objects/<model("hcs_sudameris.hcs_sudameris"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('hcs_sudameris.object', {
#             'object': obj
#         })

# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError, Warning
from datetime import datetime
import logging, json, requests

_logger = logging.getLogger(__name__)

_TipoCobro = [('1', 'Sueldo'), ('2', 'Aguinaldo'), ('3', 'Anticipo de Sueldo'),
('4', 'Otras Remuneraciones'), ('7', 'Acreditación Tarjeta Prepaga'), ('8', 'Pago de Licencias')]

_Moneda = [('6900', 'Guaraníes'), ('1', 'Dólares Americanos')]

_ModalidadPago = [('20', 'Débito en Cta. Cte'), ('21', 'Débito Caja de Ahorro')]

_EstadoMovimiento = [('preliquidacion', 'Preliquidación'), ('aprobado', 'Aprobado'), ('enproceso', 'En Proceso'), ('cancelado', 'Cancelado'), ('liquidado', 'Liquidado')]


class sudameris_employee_salary_movement(models.Model):
  _name = 'sudameris_employee_salary_movement'
  _description = 'Movimientos de salario del empleado'
  _rec_name = 'empleado'

  empleado = fields.Many2one(string='Empleado', comodel_name='hr.employee')
  identification_id = fields.Char(string='Nº identificación', related='empleado.identification_id', required=True)
  moneda = fields.Selection(selection=_Moneda, strsng="Moneda", related='empleado.tipo_moneda', readonly=True)
  salario_bruto_def = fields.Float(string="Salario del empleado", digits=(18, 2), related='empleado.salario_bruto', readonly=True)
  salario_importe = fields.Float(string="Salario a pagar", digits=(18, 2))
  tipo_cobro = fields.Selection(selection=_TipoCobro, string="Tipo de Cobro", default="1")
  fecha_pago = fields.Date(string="Fecha de pago", default=lambda s: fields.Date.context_today(s))
  modalidad_pago = fields.Selection(string="Modalidad de pago", selection=_ModalidadPago, default="21")
  codigo_operacion = fields.Char(string="Operación")
  codigo_suboperacion = fields.Char(string="Suboperación")
  tipo_operacion = fields.Char(string="Tipo de Operación")
  referencia = fields.Char(string="Referencia")
  state = fields.Selection(string="Estado", selection=_EstadoMovimiento, default='preliquidacion')

  def btn_aprobar(self):
    for rec in self:
      rec.state = 'aprobado'
      
  def btn_preliquidacion(self):
    for rec in self:
      rec.state = 'preliquidacion'

  # Hacer funcion async para obtener la respuesta
  def obtener_token(self):
    #import wdb
    #wdb.set_trace()
    config_parameter = self.env['ir.config_parameter'].sudo()
    sudameris_auth = json.loads(config_parameter.get_param('sudameris.auth'))
    # Si la fecha de hoy es mayor a la fecha de expiración
    if datetime.now() > datetime.strptime(sudameris_auth['expiration'], '%Y-%m-%d %H:%M:%S'):
      r = requests.post('https://alertaseg.com.ar:8089/api/alerta_gps/check', data={})
      return r.content
      # raise ValidationError(json.dumps(r, indent=4))
      ### Me contecto al banco y espero respuesta del mismo *CREAR CONEXION VIA POST
      #
      # Guardo los nuevos datos en el parametro
      sudameris_auth = '{"token": "TOKEN_TEST","expiration":"2021-02-01 00:00:00"}'
      config_parameter.set_param('sudameris.auth', sudameris_auth)
      sudameris_auth = json.loads(sudameris_auth)
      #
      ### Finalizo la configuración del banco
    # Siempre retorno el token valido
    return sudameris_auth

  def generar_pago(self):
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
    _txt_title = 'SUDAMERIS_ODOO_{}.txt'.format(datetime.strftime(datetime.now(), '%Y%m%d%H%M%S'))
    _txt_content = 'H;999;mail@entidad.com;6900;52000.00;1;19/05/20;202005902952101999;1;1;1982073;10;20;6900;0;0;0\n'
    for rec in self:
      if rec.state == 'aprobado':
        empleado = rec.empleado
        # Obtengo los nombres
        _nombres = empleado.nombres.split(' ')
        # Si solo tiene 1 nombre, agrego un string vacio
        if len(empleado_nombres) == 1:
          _nombres.append('')
        # Obtengo los apellidos
        _apellidos = empleado.apellidos.split(' ')
        # Si solo tiene 1 apellido, agrego un string vacio
        if len(empleado_apellidos) == 1:
          _apellidos.append('')
        # Genero el detalle con los datos del empleado
        #D;PAGO DE SALARIO VIA BANCO;APELLIDO 1;APELLIDO 2;NOMBRE 1;NOMBRE 2;586;1;111222;6900;52000.00;19/05/20;21;498154;10;6900;0;0;0;202005902952101999;1;528000.00;31/12/99
        _detalle = "D;PAGO DE SALARIO NUEVO SISTEMA;{0};{1};{2};{3};{4};{5};{6};{7};{8};{9};{10};{11};{12};{13};{14};{15};{16};{17};{18};{19};{20}\n".format(
          _apellidos[0], _apellidos[1], _nombres[0], _nombres[1],
          empleado.country_id.name, empleado.tipo_documento, empleado.identification_id,
          rec.moneda, rec.salario_importe, rec.fecha_pago, rec.modalidad_pago, empleado.numero_cuenta,
          empleado.numero_sucursal, empleado.tipo_moneda, rec.codigo_operacion, rec.tipo_operacion,
          rec.codigo_suboperacion, rec.referencia, empleado.tipo_contrato,
          empleado.salario_bruto, empleado.fecha_fin_contrato,
        )
        _txt_content += _detalle
    raise ValidationError([_txt_title, ': ', _txt_content])
    # return self.env.ref(_txt_title).report_action(self, data=_txt_content, config=False)
    # self.env.ref(_txt_title).report_action(self, data=_txt_content)
    # with open("/tmp/{}".format(_txt_title), "w") as file:
    #  file.write(_txt_content)

# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from .sudameris_api import SudamerisApi
from datetime import datetime
import logging, json

_logger = logging.getLogger(__name__)

#Referencia de códigos de datos
_TipoGrupo = [('90', 'Payroll'), ('94', 'Proveedores')]

_Moneda = [('6900', 'Guaraníes'), ('1', 'Dólares Americanos')]

_TipoDocumento = [('1', 'CEDULA DE IDENTIDAD'), ('2', 'CREDENCIAL CIVICA'), ('3', 'R.U.C.'),
('4', 'PASAPORTE'), ('5', 'DNI-DOC.NAC.IDENTID.'), ('6', 'REGISTRO DE COMERCIO'),
('7', 'LIB.DE ENROLAMIENTO'), ('10', 'GARANTIA'), ('15', 'Entidades Públicas'), 
('16', 'CARNET-INMIGRACIONES'), ('98', 'No Registra'),  ('99', 'Inst. Financieras'),
('20', 'REPRES.DIPLOMATICAS')]

_TipoContrato = [('1', 'Contrato Por Tiempo Indefinido'), ('2', 'Contrato Por Tiempo Definido')]

_EstadoEmpleado = [('borrador', 'Borrador'), ('enproceso', 'En proceso de alta'), ('listo', 'Listo')]


class hr_employee_wizard(models.TransientModel):
  _name = "hr.employee.wizard"
  _description = "HR employee wizard"
  message = fields.Text(readonly=True, store=False)

class hr_employee_sudameris_inherit(models.Model):
  _inherit = 'hr.employee'
  
  @api.onchange('nombres', 'apellidos')
  def on_change_name(self):
    for rec in self:
      rec.name = '{} {}'.format(rec.nombres, rec.apellidos)
        
  def btn_aprobar(self):
    for rec in self:
      rec.state = 'enproceso'
      
  def btn_borrador(self):
    for rec in self:
      rec.state = 'borrador'

  def btn_reiniciar(self):
    for rec in self:
      rec.numero_cuenta = None
      rec.numero_sucursal = None
      rec.nombre_cuenta = None
      rec.state = 'enproceso'
      
  def show_message(self, title, message):
    return {
      'name': title,
      'type': 'ir.actions.act_window',
      'res_model': 'hr.employee.wizard',
      'view_mode': 'form',
      'view_type': 'form',
      'context': {'default_message': message},
      'target': 'new'
    }

  @api.onchange('salario_bruto')
  def compute_wk(self):
    if self.state != 'listo': # Solo si el empleado no está listo, obtengo los kits y le asigno el kit minimo
      for kit in self.env['sudameris_employee_products'].search([('tipo', '=', 'kit')], order='salario_minimo desc'):
        if self.salario_bruto >= kit.salario_minimo:
          self._origin.wk = kit.id
          break
        
  def crear_movimientos(self):
    _changes = []
    # Obtengo el context de movimientos de salarios
    movimientos = self.env['sudameris_employee_salary_movement']
    # Obtengo los empleados seleccionados
    empleados = self.env['hr.employee'].browse(self._context.get('active_ids'))
    for rec in empleados:
      _create = True
      if rec.state == 'listo':
        list_movimientos = movimientos.search([('empleado.id', '=', rec.id)])
        for movimiento in list_movimientos:
          if datetime.now().month == movimiento.fecha_pago.month:
            _changes.append('[ATENCION]: {} ya tiene un movimiento creado para el mes actual'.format(rec.name))
            _create = False
        # Si no hay un registro, lo crea
        if _create:
          movimientos.create({
            'empleado': rec.id,
            'salario_bruto_def': rec.salario_bruto,
          })
          _changes.append('[OK]: Se creó el movimiento de {}'.format(rec.name))
      else:
        _changes.append('[ATENCION]: {} no está listo para crear movimiento de salario'.format(rec.name))
    return self.show_message('Crear movimiento de salarios', '\n'.join(_changes))

      
  def cliente_posee_cuenta(self):
    _changes = []
    # Creo la clase y le paso como parametro ir.config_parameter como sudo      
    sudamerisApi = SudamerisApi(self.env['ir.config_parameter'].sudo())
    # Obtengo los empleados seleccionados
    empleados = self.env['hr.employee'].browse(self._context.get('active_ids'))
    # Por cada empleado seleccionado
    for rec in empleados:
      if rec.state == 'borrador':
        _changes.append('[ERROR]: {} debe estar En Proceso de Alta'.format(rec.name))      
        continue
      if rec.state == 'listo' and rec.numero_cuenta != '':
        _changes.append('[ATENCION]: {} ya posee una cuenta en el banco'.format(rec.name))
        continue
      else:
        # Hago la consulta a la API
        result = sudamerisApi.ws_cliente_posee_cuenta(rec.country_id.name, rec.tipo_documento, rec.identification_id)
        for res in result:
          _valor = res["Filas"]["RepFilas.Fila"][0]["Valor"]
          if res['Descripcion'] == "CTNRO": # Número de cuenta
            rec.numero_cuenta = _valor
          if res['Descripcion'] == "Cttfir": # Sucursal
            rec.numero_sucursal = 1
          if res['Descripcion'] == "Observacion": # Descripción de la cuenta
            rec.nombre_cuenta = _valor
        # Guardo la respuestas correspondientes y marco el empleado como listo        
        rec.state = 'listo'
        _changes.append('[OK]: {} obtuvo su cuenta'.format(rec.name))
    return self.show_message('Cliente Posee Cuenta', '\n'.join(_changes))

    
  nombres = fields.Char(string="Nombre 1", required=True)
  apellidos = fields.Char(string="Apellido 1", required=True)
  tipo_documento = fields.Selection(selection=_TipoDocumento, string="Tipo de identificación", digits=(2), default="5")
  vencimiento_documento = fields.Date(string="Vencimiento de identificación")
  tipo_contrato = fields.Selection(selection=_TipoContrato, string="Tipo de Contrato", digits=(1), default="2")
  tipo_moneda = fields.Selection(string="Tipo de moneda", selection=_Moneda, default="6900")
  salario_bruto = fields.Float(string="Salario", digits=(18,2))
  codigo_direccion = fields.Integer(default=1, digits=(3))
  ciudad = fields.Integer(string="Ciudad", digits=(3), required=True)
  departamento = fields.Integer(string="Departamento", digits=(4), required=True)
  barrio = fields.Integer(string="Barrio", digits=(9), required=True)
  calle_transversal = fields.Char(string="Calle Transversal", digits=(35))
  domicilio_real = fields.Char(string="Domicilio real", digits=(50))
  nro_casa = fields.Integer(string="Numero de Casa", digits=(3))
  tipo_grupo = fields.Selection(selection=_TipoGrupo, string="Tipo de Grupo", digits=(3), default="90")
  ejecutivo = fields.Integer(string="Ejecutivo")
  fecha_ingreso = fields.Date(string="Fecha de ingreso")
  fecha_fin_contrato = fields.Date(string="Fecha de fin de contrato")
  numero_sucursal = fields.Char(string="Sucursal del Empleado")
  numero_cuenta = fields.Char(string="Número de la Cuenta", digits=(9), readonly=True)
  nombre_cuenta = fields.Char(string="Descripción de la Cuenta", digits=(30), readonly=True)
  sub_segmentacion = fields.Selection(selection=[('S', 'Crear'), ('N', 'No crear')], string="Sub segmentación", digits=(1), default="N")
  wk = fields.Many2one(string='Welcome Kit', comodel_name='sudameris_employee_products')
  state = fields.Selection(string="Estado", selection=_EstadoEmpleado, default='borrador')


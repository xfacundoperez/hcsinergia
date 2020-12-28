# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

class sudameris_salary_inherit(models.Model):
  _inherit = 'hr.employee'
  
  tpgroup = fields.Selection(selection=[('90', 'Payroll'), ('94', 'Proveedores')], string="Tipo de Grupo", digits=(3))
  ejecutivo = fields.Integer(string="Ejecutivo", compute="_field_check", store=True)
  tpcontrato = fields.Selection(selection=[('D', 'Definido'), ('I', 'Indefinido')], string="Tipo de Contrato", digits=(1))
  tdoc = fields.Selection(selection=[('10', 'DNI')], string="Tipo de identificación", digits=(2))
  vencidoc = fields.Date(string="Vencimiento de identificación")
  salario = fields.Float(string="Salario", digits=(18,2))
  coddirec = fields.Integer(default=1, digits=(3))
  fingreso = fields.Date(string="Fecha de ingreso")
  ctnro = fields.Char(string="Número de la Cuenta", digits=(9), readonly=True)
  ctnom = fields.Char(string="Descripción de la Cuenta", digits=(30), readonly=True)


class sudameris_employee_salary_movement(models.Model):
  _name = 'sudameris_employee_salary_movement'
  _description = 'Movimientos de salario del empleado'

  empleado = fields.Many2one(string='Empleado', comodel_name='hr.employee')
  # salario_def = fields.Float(string="Salario del empleado", digits=(18, 2), store=False, related=)

#class hcs_sudameris(models.Model):
#	_name = 'hcs_sudameris.hcs_sudameris'
#	_description = 'hcs_sudameris.hcs_sudameris'
#
#	name = fields.Char()
#	value = fields.Integer()
#	value2 = fields.Float(compute="_value_pc", store=True)
#	description = fields.Text()
#
#	@api.depends('value')
#	def _value_pc(self):
#	 for record in self:
#		 record.value2 = float(record.value) / 100

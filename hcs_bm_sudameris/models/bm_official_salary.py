# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError, Warning
from datetime import datetime
import logging, json, requests
_logger = logging.getLogger(__name__)


class BM_OfficialSalary(models.Model):
  _name = 'bm.official.salary'
  _description = 'Movimiento de salario del funcionaro'
  _rec_name = 'official'

  @api.depends('amount_to_pay', 'official_gross_salary')
  def _compute_amount_to_pay(self):
    for rec in self:
      rec.amount_to_pay = rec.official_gross_salary

  official = fields.Many2one('bm.official', 'Funcionario')
  official_identification_id = fields.Char(string='Nº identificación', related='official.identification_id', readonly=True)
  official_company_id = fields.Many2one('res.company', related='official.company_id', readonly=True)
  official_currency_type = fields.Selection([
      ('6900', 'Guaraníes'),
      ('1', 'Dólares Americanos')], strsng="Moneda", related='official.currency_type', readonly=True)
  official_gross_salary = fields.Float("Salario del funcionario", digits=(18, 2), related='official.gross_salary', readonly=True)
  amount_to_pay = fields.Float(string="Salario a pagar", digits=(18, 2), compute=_compute_amount_to_pay, store=True)
  charge_type = fields.Selection([
      ('1', 'Sueldo'),
      ('2', 'Aguinaldo'),
      ('3', 'Anticipo de Sueldo'),
      ('4', 'Otras Remuneraciones'),
      ('7', 'Acreditación Tarjeta Prepaga'),
      ('8', 'Pago de Licencias')], string="Tipo de Cobro", default="1")
  payment_date = fields.Date(string="Fecha de pago", default=lambda s: fields.Date.context_today(s))
  payment_mode = fields.Selection([
      ('20', 'Débito en Cta. Cte'),
      ('21', 'Débito Caja de Ahorro')], string="Modalidad de pago", default="21")
  operation_type = fields.Char(string="Tipo de Operación")
  operation_code = fields.Char(string="Operación")
  company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company)
  suboperacion_code = fields.Char(string="Suboperación")
  reference = fields.Char(string="Referencia")
  state = fields.Selection([
      ('draft', 'Preliquidación'),
      ('aproved', 'Aprobado'),
      ('check', 'En Proceso'),
      ('cancel', 'Cancelado'),
      ('done', 'Liquidado')], string="Estado", default='draft')
  movement_id = fields.Many2one('bm.official.salary.history')

  def show_message(self, title, message):
    return {
      'name': title,
      'type': 'ir.actions.act_window',
      'res_model': 'bm.official.salary.wizard',
      'view_mode': 'form',
      'view_type': 'form',
      'context': {'default_message': message},
      'target': 'new'
    }

  def btn_aprobar(self):
    for official_salary in self:
      official_salary.state = 'aproved'
      
  def btn_draft(self):
    for official_salary in self:
      official_salary.state = 'draft'

  def create_file_txt(self):
    #aproved_moves = self.search([('state', '=', 'aproved')])
    #if aproved_moves:
    #  last_movement = self.env['bm.official.salary.history'].create({'official_salary_ids': [(6, 0, aproved_moves.ids)]})
    #  for rec in aproved_moves:
    #    rec.movement_id = last_movement.id
    #    rec.state = 'check'
    # Los registros que están aprobados, los seteo en proceso
    for rec in self:
      if rec.state == 'aproved':
        rec.state = 'check'
    # Obtengo solo los ID de los que están en proceso y si hay alguno, genero el archivo de pago
    _ids = self.search([('state', 'in', ['check'])]).ids
    if _ids:
      return {
        'type': 'ir.actions.act_url',
        'url': '/web/binary_text/create_file_txt?ids={}'.format(', '.join([str(_id) for _id in _ids])),
        'target': 'self'
      }
    else:
      return self.show_message('Generar Pago', 'No se generó ningun pago, los registros no están aprovados')


class BM_OfficialSalaryHistory(models.Model):
  _name = 'bm.official.salary.history'
  _description = 'Historial de Movimiento de salario'

  def _compute_name(self):
    for rec in self:
      rec.name = "Movimiento N°{}".format(rec.id)

  name = fields.Char(compute="_compute_name")
  official_salary_ids = fields.Many2many('bm.official.salary', 'official_salary_rel', 'official_id')

  #def create_file_txt(self, last_movement=None):
  #  return True
  #  if not last_movement:
  #    last_movement = self.env['bm.official.salary.history'].search('id', 'in', self.env._context.get('active_ids'))

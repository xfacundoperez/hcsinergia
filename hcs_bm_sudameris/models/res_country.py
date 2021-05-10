from odoo import models, fields


class BM_res_country(models.Model):
  _inherit = "res.country"

  code_number = fields.Integer()

class BM_res_country_departament(models.Model):
  _name = "res.country.departament"
  
  name = fields.Char(string='Nombre del departamento', required=True)
  code = fields.Char(string='Código de departamento', required=True)
  state_id = fields.Many2one(string='Provincia', comodel_name='res.country.state', required=True)

  _sql_constraints = [
      ('state_id_code_uniq', 'unique(state_id, code)', 'El código del departamento debe ser único por ciudad. !')
  ]


class BM_res_country_neighborhood(models.Model):
  _name = "res.country.neighborhood"
  
  name = fields.Char(string='Nombre del barrio', required=True)
  code = fields.Char(string='Código de barrio', required=True)
  departament_id = fields.Many2one(string='Departamento', comodel_name='res.country.departament', required=True)

  _sql_constraints = [
      ('departament_id_code_uniq', 'unique (departament_id, code)', 'El código del barrio debe ser único por departamento. !')
  ]

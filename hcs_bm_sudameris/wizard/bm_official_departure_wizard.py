# -*- coding: utf-8 -*-
from odoo import api, fields, models
from datetime import datetime
import wdb

DEPARTURE_REASONS = [('medical', 'Medica'), ('fired', 'Despido'), ('resigned', 'Renuncia'), ('retired', 'Retirado')]


class BMOfficialDepartureWizard(models.TransientModel):
    _name = 'bm.official.departure.wizard'
    _description = "BM Official Departure Wizard"

    def button_save(self):
        official = self.env['bm.official'].browse(self.env.context.get('active_id'))
        departure_obj = self.env['bm.official.departure']
        departure_last_reg = departure_obj.search(['&', ('official_identification_id', '=', official.identification_id), ('state', '=', 'active')], order='id desc', limit=1)
        return departure_obj.create({
            'official': official.id,
            'departure_reason': self.departure_reason,
            'departure_description': self.departure_description,
            'departure_start': self.departure_start,
            'departure_end': self.departure_end,
        })
        
    departure_reason = fields.Selection(DEPARTURE_REASONS, string="Motivo de salida", copy=False, tracking=True, required=True, default="medical")
    departure_description = fields.Text(string="Salida: Información adicional", copy=False, tracking=True)
    departure_start = fields.Date(string="Fecha de Salida", default=lambda self: datetime.now().date(), copy=False, required=True)
    departure_end = fields.Date(string="Fecha de Retorno", copy=False)

    @api.onchange('departure_reason')
    def on_change_departure_reason(self):
        if self.departure_reason == 'medical':
            self.departure_end = self._origin.departure_end
        else:
            self.departure_end = None

    @api.onchange('departure_end')
    def on_change_departure_end(self):
        if self.departure_end:
            if self.departure_end < self.departure_start:
                self.departure_end = self.departure_start

    @api.onchange('departure_start')
    def on_change_departure_start(self):
        if self.departure_start:
            if self.departure_end:
                if self.departure_start > self.departure_end:
                    self.departure_end = None
        else:
            self.departure_end = None

# -*- coding: utf-8 -*-
from odoo import api, fields, models


class BMOfficialWizard(models.TransientModel):
    _name = "bm.official.wizard"
    _description = "BM Official Wizard"

    message = fields.Text(readonly=True, store=False)


class BMOfficialWizardRejectCAM(models.TransientModel):
    _name = 'bm.official.wizard.rejectcam'
    _description = "BM Official Wizard Rechazar CAM"

    def button_save(self):
        official = self.env['bm.official'].browse(self.env.context.get('active_id'))
        official.reject_reason = self.reject_reason
        official.state = 'error'
        return True
    
    reject_reason = fields.Text('Motivo de rechazo')

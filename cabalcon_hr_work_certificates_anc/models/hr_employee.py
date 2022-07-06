# -*- coding: utf-8 -*-

from odoo import models, fields, _, api
from odoo.exceptions import ValidationError


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    def print_work_certificates_anc(self):
        return self.env.ref('cabalcon_hr_work_certificates_anc.action_work_certificates_anc').report_action(self)

    
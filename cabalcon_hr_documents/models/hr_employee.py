# -*- coding: utf-8 -*-
from dateutil.relativedelta import relativedelta
from odoo import models, fields, _, api


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    document_type = fields.Many2one('hr.employee.document.type', string='Tipo de documento', help="Tipo de documento", required=True,  domain=[('identity', '=', 'True')])


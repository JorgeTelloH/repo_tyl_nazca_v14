from odoo import fields, models, api


class Emoloyee(models.Model):
    _inherit = 'hr.employee'

    another_companies = fields.Boolean(string='Percibe remuneraciones de otras empresas')

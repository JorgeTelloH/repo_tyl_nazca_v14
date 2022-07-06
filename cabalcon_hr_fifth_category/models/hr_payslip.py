from odoo import fields, models, api
from odoo.exceptions import ValidationError


class Payslip(models.Model):
    _inherit = 'hr.payslip'

    # Se le pasa lista de codigos de las reglas que quiere sumar
    def _get_salary_lines_total(self, list_of_codes):
        lines = self.line_ids.filtered(lambda line: line.code in list_of_codes)
        return sum([line.total for line in lines])

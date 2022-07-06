# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class Job(models.Model):
    _inherit = "hr.job"

    occupational_category_id = fields.Many2one('hr.occupational.category', string='Categoría ocupacional')
    min_wage = fields.Float('Salario mínimo')
    max_wage = fields.Float('Salario máximo')

    @api.constrains('min_wage', 'max_wage')
    def check_wage(self):
        for job in self:
            if job.min_wage > 0 and job.max_wage > 0:
                if job.min_wage > job.max_wage:
                    raise ValidationError("El salario mínimo no puede ser mayor que el salario máximo")


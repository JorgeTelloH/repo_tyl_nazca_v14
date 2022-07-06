# -*- coding:utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class HrEmployeeHealthEntity(models.Model):
    _name = 'hr.employee.health.entity'
    _description = 'Entidades Aseguradoras de salud'
    _sql_constraints = [
        ('name_uniq', 'UNIQUE(code)', 'El código debe ser único!'),
    ]

    name = fields.Char('Nombre', required=True)
    code = fields.Char(string='Código', required=True)
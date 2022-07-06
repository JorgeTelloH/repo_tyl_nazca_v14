from odoo import fields, models, api


class Roll(models.Model):
    _name = 'operations.roll'
    _description = 'Roles'
    _sql_constraints = [
        ('code', 'unique (code)', 'El código del roll debe ser único!')
    ]

    code = fields.Char(string='Código', required=True)
    name = fields.Char(string='Nombre', required=True)

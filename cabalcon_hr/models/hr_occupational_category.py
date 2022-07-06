from odoo import fields, models, api


class OccupationalCategory(models.Model):
    _name = 'hr.occupational.category'
    _description = 'Categoría ocupacional del trabajador'
    _sql_constraints = [
        ('code', 'unique (code)', 'El código de la categoría ocupacional debe ser único!')
    ]

    name = fields.Char(string='Nombre', required=True)
    code = fields.Char(string='Código', required=True)
    private_sector = fields.Boolean(string='Sector privado',required=True)
    public_sector = fields.Boolean(string='Sector publico',required=True)
    other_entities = fields.Boolean(string='Otras entidades',required=True)

    active = fields.Boolean(string='Active',  default=True)
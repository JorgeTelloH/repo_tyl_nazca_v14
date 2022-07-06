from odoo import fields, models, api


class Partner(models.Model):
    _inherit = "res.partner"

    employee_id = fields.Many2one("hr.employee", string="Empleado")

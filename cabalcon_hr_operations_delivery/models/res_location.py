
from odoo import api,fields,models,_
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError


class Locations(models.Model):
    _inherit = "res.location"

    department_id = fields.Many2one('hr.department', 'Departamento')
    # TODO poner el dominio cuando se agregue la multi companñia
    # domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
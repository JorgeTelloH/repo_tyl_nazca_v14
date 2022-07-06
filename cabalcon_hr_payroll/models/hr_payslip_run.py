from odoo import fields, models, api
from odoo.exceptions import UserError


class Subtype(models.Model):
    _name = 'hr.payslip.subtype.payroll'
    _description = 'Subtipo de Planilla de Haberes'

    name = fields.Char('Nombre', required=True)
    code = fields.Char(string='Código', required=True)
    salary_rule_ids = fields.Many2many('hr.salary.rule', string='Reglas')


class PayslipRun(models.Model):
    _inherit = 'hr.payslip.run'

    def action_print_txt(self):
        action = {
            'type': 'ir.actions.act_window',
            'name': 'Exportar fichero Txt',
            'view_mode': 'form',
            'view_id': self.env.ref('cabalcon_hr_payroll.export_txt_wizard_wizard_view_form').id,
            'res_model': 'export.txt.wizard',
            'context': {
                'default_date_from': self.date_start,
                'default_date_to': self.date_end,
            },
            'target': 'new',
        }
        return action


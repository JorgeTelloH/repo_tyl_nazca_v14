# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class HrLiquidationWizard(models.TransientModel):
    _name = 'hr.liquidation.wizard'

    def set_domain(self):
        return [('id', 'in', self.env.context.get('active_ids'))]

    option = fields.Selection(string='Opción',
                              selection=[('all', 'Todos'),
                                         ('selectd', 'Los seleccionados')],
                              default='all')
    employee_ids = fields.Many2many('hr.employee', string='Empleado', domain=set_domain)
    social_benefit_id = fields.Many2one('hr.social.benefits', string='Social benefit', default=lambda self: self.env.context.get('social_benefit_id'))

    def action_print(self):
        self.ensure_one()
        [data] = self.read()

        datas = {
            'form': data,
        }
        return self.env.ref('cabalcon_hr_social_benefits.action_liquidation_report').report_action(self, data=data)

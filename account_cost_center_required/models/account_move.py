# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class AccountMove(models.Model):
    _inherit ='account.move'

    def _post(self, soft=True):
        for move_line in self.invoice_line_ids:
            if self.company_id.account_cost_center_select == 'posted' and not move_line.cost_center_id:
                raise ValidationError(_('Debe colocar el Centro de Costo en el Detalle'))
            if self.company_id.account_cost_center_select == 'always' and not move_line.cost_center_id:
                raise ValidationError(_('Debe colocar el Centro de Costo en el Detalle'))
        return super(AccountMove, self)._post(soft)


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.constrains('cost_center_id')
    def check_cost_center_id(self):
        for rec in self:
            if not rec.move_id.invoice_line_ids:
                if rec.company_id.account_cost_center_select == 'always' and not rec.cost_center_id:
                    raise ValidationError(_('Debe colocar el Centro de Costo en el Detalle'))
            else:
                for inv_line in rec.move_id.invoice_line_ids:
                    if rec.company_id.account_cost_center_select == 'always' and not inv_line.cost_center_id:
                        raise ValidationError(_('Debe colocar el Centro de Costo en el Detalle'))


# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class AccountPayment(models.Model):
    _inherit = "account.payment"

    expense_id = fields.Many2one('account.expense', string='Gasto')

    def cancel(self):
        res = super(AccountPayment, self).cancel()
        for rec in self:
            if rec.expense_id:
                if rec.expense_id.state in ['draft','approved','refused']:
                    if rec.expense_id.state in ['draft', 'approved']:
                        rec.expense_id.get_expense_amount()
                else:
                    raise ValidationError(_('No se puede cancelar un pago asociado a un Gasto que esta en proceso o realizado'))
        return res

    def action_post(self):
        res = super(AccountPayment, self).action_post()
        for rec in self:
            if rec.expense_id:
                if rec.expense_id.state in ['draft','approved','rembolso','cobro']:
                    rec.expense_id.get_expense_amount()
                else:
                    raise ValidationError(_('No se puede validar un pago asociado a un Gasto que esta en proceso o realizado'))
        return res
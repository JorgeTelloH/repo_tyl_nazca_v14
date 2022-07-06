# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class AccountMove(models.Model):
    _inherit ='account.move'

    def _post(self, soft=True):
        for move_line in self.invoice_line_ids:
            if self.company_id.account_analytic_select == 'posted' and not move_line.analytic_account_id:
                raise ValidationError(_('Debe colocar la Cuenta Analítica en el Detalle'))
            if self.company_id.account_analytic_select == 'always' and not move_line.analytic_account_id:
                raise ValidationError(_('Debe colocar la Cuenta Analítica en el Detalle'))
        return super(AccountMove, self)._post(soft)


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.constrains('analytic_account_id')
    def check_analytic_account_id(self):
        for rec in self:
            if not rec.move_id.invoice_line_ids:
                if rec.company_id.account_analytic_select == 'always' and not rec.analytic_account_id:
                    raise ValidationError(_('Debe colocar la Cuenta Analítica en el Detalle'))
            else:
                for inv_line in rec.move_id.invoice_line_ids:
                    if rec.company_id.account_analytic_select == 'always' and not inv_line.analytic_account_id:
                        raise ValidationError(_('Debe colocar la Cuenta Analítica en el Detalle'))


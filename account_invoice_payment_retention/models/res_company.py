# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ResCompany(models.Model):
    _inherit = "res.company"

    retention_account_id = fields.Many2one(comodel_name="account.account",
        string="Cuenta de Retención", domain=[("user_type_id.type", "=", "other")],
        help="Cuenta de Retención usada en caso de Retención de Pagos",
    )

    @api.constrains("retention_account_id")
    def _check_retention_account_id(self):
        for rec in self.filtered("retention_account_id"):
            if not rec.retention_account_id.reconcile:
                raise ValidationError(
                    _("La Cuenta de Retención debe estar configurada para permitir la conciliación")
                )

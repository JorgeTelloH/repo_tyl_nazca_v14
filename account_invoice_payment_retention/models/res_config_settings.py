# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    group_payment_retention = fields.Boolean(string="Activar Retención de pagos en Facturas",
        implied_group="account_invoice_payment_retention.group_payment_retention",
    )
    retention_account_id = fields.Many2one(comodel_name="account.account",
        related="company_id.retention_account_id", string="Cuenta de Retención",
        readonly=False, help="Cuenta de Retención usada en caso de Retención de Pagos",
    )

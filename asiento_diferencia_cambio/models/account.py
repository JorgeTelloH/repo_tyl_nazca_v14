# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class AccountAccount(models.Model):
    _inherit = "account.account"

    dc_account = fields.Boolean(string='Genera Dif.Cambio mensual', default=False,
                                help="Activar para que sea tomado en cuenta en la generacion de la Diferencia de Cambio mensual")
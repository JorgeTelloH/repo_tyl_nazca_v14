# -*- coding: utf-8 -*-
from odoo import api,fields,models,_
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError
import re


class AccountMove(models.Model):
    _inherit = "account.move"

    def action_send_masive_cancel(self):
        self.button_draft()
        self.cuotas_ids.unlink()
        self.with_context(force_delete=True).unlink()
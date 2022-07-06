# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_send_masive_electronic(self):
        for inv in self:
            if inv.edi_web_services_to_process not in ['', False] or inv.state != 'draft':
                if inv.edi_state == 'to_send':
                    inv.action_process_edi_web_services()

        return


# -*- encoding: utf-8 -*-
from odoo import api, fields, models, tools, SUPERUSER_ID

class Lead(models.Model):
    _inherit = "crm.lead"

    def toggle_active(self):
        """ When archiving: mark probability as 0. When re-activating
        update probability again, for leads and opportunities. """
        res = super(Lead, self).toggle_active()
        activated = self.filtered(lambda lead: lead.active)
        archived = self.filtered(lambda lead: not lead.active)
        if activated:
            activated.write({'lost_reason': False})
            activated._compute_probabilities()
        if archived:
            if not archived.stage_id.is_won:
                archived.write({'probability': 0, 'automated_probability': 0})
            else:
                archived.write({'lost_reason': False})
                archived.write({'probability': 100, 'automated_probability': 100})
        return res
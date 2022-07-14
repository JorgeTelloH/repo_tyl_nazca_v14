import logging

from odoo import models, fields, api

class Users(models.Model):
    _inherit = 'res.users'

    @api.model
    def create(self, vals):
        contact_ids = self.env.ref('contacts.menu_contacts').ids
        tms_ids = self.env.ref('tms.menu_tms').ids
        mailing_ids = self.env.ref('utm.menu_link_tracker_root').ids
        hr_ids = self.env.ref('hr.menu_hr_root').ids
        vals.update({'access_menu_ids':[(6,0,[contact_ids[0],tms_ids[0],mailing_ids[0],hr_ids[0]])]})

        res = super(Users, self).create(vals)

        return res



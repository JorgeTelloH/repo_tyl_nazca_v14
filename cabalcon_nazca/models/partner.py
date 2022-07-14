import logging

from odoo import models, fields, api

class Partner(models.Model):
    _inherit = 'res.partner'

    kw_address_id = fields.Many2many('kw.address', 'res_partner_kw_address_rel', 'partner_id',
                                  'kw_address_id', string="Direccion")

    date_partner = fields.Date(string='Fecha')

    driver_license = fields.Char(string='Nro Licencia')
    license_type = fields.Many2one('driver.license', string='Tipo de licencia')
    license_expiration = fields.Date(string='Fecha de caducidad')
    is_driver = fields.Boolean(string="Es coductor")

    @api.onchange("category_id")
    def _onchange_category_id(self):
        driver = False
        if self.category_id:
            for catg in self.category_id:
                if catg.is_driver:
                    driver =True
        self.is_driver = driver
        return



class PartnerCatalog(models.Model):
    _inherit = 'res.partner.category'


    active_company = fields.Boolean(string="Activar para compañia")

    active_contac = fields.Boolean(string="Activar para contacto")

    is_driver = fields.Boolean(string="Es coductor")


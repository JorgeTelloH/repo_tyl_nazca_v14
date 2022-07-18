import logging

from odoo import models, fields, api

class Address(models.Model):
    _name = 'driver.license'

    name = fields.Char('Tipo de licencia')
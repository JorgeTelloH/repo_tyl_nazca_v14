# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class DocumentType(models.Model):
    _name = 'hr.employee.document.type'
    _description = 'Tipos de documentos'

    code = fields.Char(string='Código', required="True")
    cod_afp_net = fields.Char(string='Código AFP Net')
    name = fields.Char(string='Nombre corto', required=True)
    desc = fields.Char(string='Descripción', required="True")

    identity = fields.Boolean(string='Es Documento de identidad?', help='Usado para definir si es un documento de identidad')
    active = fields.Boolean(string='Active',  default=True)

    def unlink(self):
        for document in self:
            contracts = self.env['hr.employee'].search([('document_type', '=', document.id)])
            if len(contracts) > 0:
                raise ValidationError('No puedes eliminar este tipo de documento porque está siendo usado')
        return super(DocumentType, self).unlink()






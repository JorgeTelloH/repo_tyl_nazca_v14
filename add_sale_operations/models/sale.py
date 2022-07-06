# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import date

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    date_order = fields.Date(string='Fecha Pedido', required=True, readonly=True, index=True, default= fields.Date.today(),
        states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})
    employee_operative = fields.Many2one('hr.employee', string='Personal Operacional', required=True)
    type_order = fields.Selection([
        ('normal', 'Normal'), ('internet', 'Canal Digital'),
        ('pack', 'Pack'), ('hpack', 'Pack heredado'),
        ('return', 'Retorno')], string='Tipo', readonly=True, index=True, 
        states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, default='normal', required=True)
    parent_id = fields.Many2one('sale.order', string='Nro Pedido Pack', index=True, readonly=True,
        states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
        domain=[('type_order', '=','pack'), ('state', 'in',('sale','done')),('is_pack_usable','=',True)])
    #Se trae el campo de "user_id" para activar el readonly
    user_id = fields.Many2one('res.users', string='Vendedor', index=True, track_visibility='onchange', readonly=True, required=True,
        states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, default=lambda self: self.env.user)
    #Se trae el campo de "payment_term_id" para activar el readonly
    payment_term_id = fields.Many2one('account.payment.term', string='Plazo de Pago',  readonly=True,
        states={'draft': [('readonly', False)], 'sent': [('readonly', False)]} )
    is_pack_usable = fields.Boolean(string='Es pack usable', default=False)


    #Se obtiene el dato del Cliente para heredarlo en el SO hijo
    @api.onchange('parent_id')
    def _change_parent_id(self):
        for order in self:
            if order.parent_id:
                order.partner_id = order.parent_id.partner_id

    @api.onchange('type_order')
    def _change_type_order(self):
        for order in self:
            order.parent_id = False
            if order.type_order == 'hpack':
                order.global_discount_type = 'percent'
                order.global_discount_rate = 100

    def _action_confirm(self):
        res = super()._action_confirm()

        # if self.env.context.get('send_email'):
        #     self.force_quotation_send()

        for order in self:
            if order.type_order == 'hpack':
                #Deshabilita el uso del pack en uso el cual ha sido asignado al SO actual
                so_obj = self.env['sale.order'].search([('id', '=',order.parent_id.id)])
                update_so = {'is_pack_usable': False}
                so_obj.write(update_so)

        return res

    def _prepare_confirmation_values(self):
        res = super()._prepare_confirmation_values()
        if self.type_order == 'hpack':
            res = {
                'state': 'done',
                'confirmation_date': fields.Datetime.now()
            }
        else:
            if self.type_order == 'pack':
                res ={
                    'state': 'sale',
                    'is_pack_usable': True,
                    'confirmation_date': fields.Datetime.now()
                }
            else:
                res = {
                    'state': 'sale',
                    'confirmation_date': fields.Datetime.now()
                }
        return res

    @api.onchange('partner_id')
    def _change_partner_id(self):
        for rec in self:
            #v_dato = ''
            if rec.type_order == 'hpack' and rec.partner_id:
                v_dato = rec.parent_id.employee_operative
            else:
                v_dato = rec.partner_id.employee_operative
            rec.employee_operative = v_dato

            if rec.type_order == 'hpack' and rec.partner_id and rec.parent_id.partner_id != rec.partner_id :
                rec.parent_id = False


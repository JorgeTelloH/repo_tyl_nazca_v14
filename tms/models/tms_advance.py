# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.tools import float_compare

class TmsAdvance(models.Model):
    _name = 'tms.advance'
    #_inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description = 'Adelantos por gastos de viaje'
    _order = "name desc, date desc"


    @api.depends('advance_payment_ids.amount', 'advance_payment_ids.state')
    def _amount_all_payment(self):
        v_amount_paid = 0
        v_amount_pending = 0
        for line in self.advance_payment_ids:
            if line:
                if line.state != 'cancelled':
                    v_amount_paid = v_amount_paid + line.amount
        v_amount_pending = (self.amount - v_amount_paid)

        self.update({
            'amount_paid': v_amount_paid,
            'amount_pending': v_amount_pending,
        })

        if self.state == 'contabilized' and v_amount_pending != 0.0:
            #Obtener mediante query
            query = """UPDATE tms_advance set state = 'realized' 
                    where """
            query += " id = %s " % (self.id)
            self.env.cr.execute(query)


    name = fields.Char(string='Adelanto', required=True, readonly=True, index=True, 
        states={'draft': [('readonly', False)]}, default='Nuevo')
    route_operation_id = fields.Many2one('tms.route.operation', string='Operación por Tramo', required=True, readonly=True, index=True,
        states={'draft': [('readonly', False)]})
    operation_type_id = fields.Many2one(related="route_operation_id.operation_type", string='Tipo de Operación', readonly=True, store=True)
    cost_ppto_operation = fields.Float(related="route_operation_id.cost_ppto_total", string='Costo de Operación', readonly=True, store=True)
    travel_route_id = fields.Many2one(related="route_operation_id.travel_route_id", string='Tramo de Viaje', readonly=True, store=True)
    travel_id = fields.Many2one(related="route_operation_id.travel_id", string='Viaje', readonly=True, store=True)
    company_id = fields.Many2one('res.company', string="Empresa", default=lambda self: self.env.user.company_id)
    state = fields.Selection(
        [('draft', 'Borrador'),
         ('approved', 'Aprobado'),
         ('realized', 'Realizado'),
         ('contabilized', 'Contabilizado'),
         ('cancel', 'Cancelado')],
        readonly=True, default='draft', index=True, string='Estado')
    date = fields.Date(string='Fecha', required=True, default=fields.Date.context_today, readonly=True, states={'draft': [('readonly', False)]})
    #vendor_id = fields.Many2one(related="route_operation_id.vendor_id", string='Proveedor', readonly=True, store=True)
    vendor_id = fields.Many2one('res.partner', domain=[('supplier', '=', True)], compute='_get_vendor_operation', string='Proveedor', readonly=True, store=True)
    currency_id = fields.Many2one(related="route_operation_id.currency_id", string='Moneda', readonly=True, store=True)
    amount = fields.Monetary(string='Monto', required=True, readonly=True, states={'draft': [('readonly', False)]})
    amount_paid = fields.Monetary(string='Monto Pagado', compute='_amount_all_payment', store=True)
    amount_pending = fields.Monetary(string='Monto Pendiente', compute='_amount_all_payment', store=True)
    notes = fields.Text(string='Notas',readonly=True, states={'draft': [('readonly', False)]})
    #payment_move_id = fields.Many2one('account.move', string="Entrada de pago", readonly=True, domain=[('state', '!=', 'draft')])
    #payment_ref = fields.Char(related="payment_move_id.ref", string='Referencia de pago')
    #paid = fields.Boolean(string='Pagado',compute='_compute_paid', readonly=True, store=True)
    account_bank = fields.Many2one('res.partner.bank', string='Cta Bancaria', required=True, readonly=True, states={'draft': [('readonly', False)]})
    bank_name = fields.Many2one(related="account_bank.bank_id", string='Banco', readonly=True, store=True)
    allow_other_receiver = fields.Boolean(string='Otro Receptor?', default=False, readonly=True, states={'draft': [('readonly', False)]})
    other_receiver = fields.Char(string='Otro Receptor')
    other_acc_bank = fields.Char(string='Cta Bancaria Otro Receptor')
    advance_payment_ids = fields.One2many('account.payment', 'advance_id', 'Pago de Adelanto', ondelete='cascade', copy=False,
        readonly=True, states={'realized': [('readonly', False)]}, domain=[('is_advance_payment', '=', True)])
    able_cancel_advance_realized = fields.Boolean(compute='set_access_cancel_advance_realized', string='Usuario puede Cancelar Adelanto Realizado?')
    #Capturar el Diario por defecto asociado para la moneda
    journal_id = fields.Many2one('account.journal', compute='_value_journal_id', 
        string='Diario predeterminado', domain=[('type', 'in', ['bank','cash'])], store=True)
    #El Adelanto se calculara luego de Aprobado
    advance_percentage = fields.Float(string='% Adelanto', default=0, readonly=True, group_operator = 'avg')
    acc_number_cci = fields.Char(related="account_bank.acc_number_cci", string='Nro Cta Interbancaria', readonly=True, store=True)
    vendor_type = fields.Char(related="route_operation_id.vendor_type", string="Tipo Proveedor de Operación", readonly=True, store=True)


    @api.depends('currency_id')
    def _value_journal_id(self):
        #Si la moneda actual es igual a la moneda company
        if self.currency_id == self.env.user.company_id.currency_id:
            rec_journal = self.env['account.journal'].search([('type','in', ('bank','cash')), ('active','=', True), ('currency_id','=',None)], limit=1)
            if rec_journal:
                self.journal_id = rec_journal.id
        else:
            rec_journal2 = self.env['account.journal'].search([('type','in', ('bank','cash')), ('active','=', True), ('currency_id','=', self.currency_id.id)], limit=1)
            if rec_journal2:
                self.journal_id = rec_journal2.id

    def set_access_cancel_advance_realized(self):
        self.able_cancel_advance_realized = self.env['res.users'].has_group('tms.group_allow_cancel_advance_realized')

    @api.depends('route_operation_id')
    def _get_vendor_operation(self):
        if self.operation_type_id and self.operation_type_id.vehicle_required == True: #Si es flete, entonces toma el proveedor del conductor
            self.vendor_id = self.route_operation_id.vendor_driver_id
        else: #Caso contrario, toma el proveedor de la operacion
            self.vendor_id = self.route_operation_id.vendor_id

    @api.model
    def create(self, vals):
        if vals.get('name','Nuevo') == 'Nuevo':
            if 'company_id' in vals and vals['company_id']:
                vals['name'] = self.env['ir.sequence'].with_context(force_company=vals['company_id']).next_by_code('tms.advance') or 'Nuevo'
            else:
                vals['name'] = self.env['ir.sequence'].next_by_code('tms.advance') or 'Nuevo'
        result = super(TmsAdvance, self).create(vals)
        #Asigna Adelanto
        result.route_operation_id.able_advance = True
        #Cerrar Adelanto si es tercero
        if result.route_operation_id.vendor_type == 'tercero':
            result.route_operation_id.allow_advance = False
        return result

    def action_approve(self):
        for rec in self:
            if rec.amount <= 0:
                raise ValidationError(
                    _('Debe ingresar un monto mayor a cero!'))

            #Ini Solo permitir un Adelanto
            other_advance = self.env['tms.advance'].search([
                ('route_operation_id','=', rec.route_operation_id.id),
                ('id','!=',rec.id),
                ('state','!=','cancel'),
                ])
            if other_advance:
                #Preguntar si hay mas de 01 adelanto para el caso de tercero
                if rec.route_operation_id.vendor_type and rec.route_operation_id.vendor_type == 'tercero':
                    raise ValidationError(
                        _('No puede generar más de un Adelanto para la %s \n Por favor validar!')%(rec.route_operation_id.name))
            #Fin Solo permitir un Adelanto

            v_amount_max = ((rec.route_operation_id.cost_ppto_total *  rec.route_operation_id.percent_max_advance) / 100)

            if rec.amount > 0 and rec.amount > v_amount_max:
                raise ValidationError(
                    _('El monto del Adelanto ingresado ha excedido del Monto Max de Adelanto! \n'
                        'Monto Max. Adelanto: %s.') % (str(v_amount_max) +' '+ rec.currency_id.currency_unit_label))

            #Calcular el porcentaje
            if rec.cost_ppto_operation > 0:
                rec.advance_percentage = ((rec.amount * 100)/ rec.cost_ppto_operation)
            rec.state = 'approved'


    def action_realize(self):
        for rec in self:
            rec.state = 'realized'

    def action_contabilize(self):
        for rec in self:
            #Buscamos si hay Pagos en cualquier estado menos cancelados
            pay_draft_advances = rec.advance_payment_ids.search([
                ('state', '!=', 'cancelled'),
                ('advance_id', '=', rec.id)])
            if len(pay_draft_advances) <= 0:
                raise ValidationError( _(
                    "No hay registro de Pago para el adelanto: '%s' \n"
                    "Por favor, registre el Pago para continuar.") % (
                    rec.name))

            precision = self.env['decimal.precision'].precision_get('Account')
            if float_compare(rec.amount, rec.amount_paid, precision_digits=precision) != 0:
                raise ValidationError(_(
                    "Hay una diferencia de %s \n"
                    "respecto al monto del adelanto: '%s'") % (
                    str(rec.amount_pending) +' '+ rec.currency_id.currency_unit_label,
                    rec.name))

            #Buscamos si hay Pagos en Borrador, si lo hubiera se pedira que lo confirmen o anulen
            pay_draft_advances = rec.advance_payment_ids.search([
                ('state', '=', 'draft'),
                ('advance_id', '=', rec.id)])
            if len(pay_draft_advances) >= 1:
                raise ValidationError(_(
                    "Existen Pagos pendientes de Confirmar \n"
                    "revisar el adelanto: '%s'") % (
                    rec.name))

            rec.state = 'contabilized'

    def action_cancel(self):
        for rec in self:
            if rec.state == 'realized' and rec.able_cancel_advance_realized != True:
                raise ValidationError(
                    _('No se puede cancelar este Adelanto, por estar Realizado. \n Solo podrá hacerlo si tiene el permiso activado.'))

            if rec.state == 'contabilized' and rec.able_cancel_advance_realized != True:
                raise ValidationError(
                    _('No se puede cancelar este Adelanto, por estar Contabilizado. \n Solo podrá hacerlo si tiene el permiso activado.'))

            #Buscamos si hay Pagos no cancelados, si lo hubiera se pedira que lo anulen
            payed_draft_advances = rec.advance_payment_ids.search([
                ('state', '!=', 'cancelled'),
                ('advance_id', '=', rec.id)])
            if len(payed_draft_advances) >= 1:
                raise ValidationError(_('Existen Pagos de Adelantos no Anulados, \n Debe Anularlos para poder Cancelar el Adelanto.'))

            #Si cancelamos 01 adelanto y es tercero, entonces permitir Adelanto
            if rec.route_operation_id.vendor_type == 'tercero':
                rec.route_operation_id.allow_advance = True

            rec.state = 'cancel'

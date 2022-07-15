# -*- coding: utf-8 -*-

from odoo import api, fields, tools, models, _
from odoo.exceptions import ValidationError, UserError, AccessError
from datetime import datetime
import dateutil.parser

#Estados del Viaje
T_STATES = [('draft','Borrador'),('planned','Planificado'),('programmed','Programado'),('started','En Curso'),('finished','Terminado'),('canceled','Cancelado')]
#Estados de Operaciones
O_STATES = [('draft','Borrador'),('planned','Planificado'),('programmed','Programado'),('started','En Curso'),('finished','Terminado'),('canceled','Cancelado')]
#Colores
color_white='#FFFFFF'
color_green='#49C909'


class TmsRouteService(models.Model):
    _name = 'tms.route.operation'
    #_inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description = 'Operaciones por Tramo'
    _order = "name desc"

    name = fields.Char(string= 'Operacion por Tramo', required=True, readonly=True, index=True, 
        states={'draft': [('readonly', False)]}, default='Nuevo')
    sequence = fields.Integer(string='Secuencia', default=10)
    operation_type = fields.Many2one('tms.route.operation.type', string="Tipo de Operación", required=True, 
        readonly=True, states={'draft': [('readonly', False)]})
    vendor_required = fields.Boolean(related="operation_type.vendor_required", string='Requiere Proveedor', readonly=True, store=True)
    tracking_required = fields.Boolean(related="operation_type.tracking_required", string='Requiere Tracking', readonly=True, store=True)
    company_id = fields.Many2one('res.company', string="Empresa", default=lambda self: self.env.user.company_id)
    state = fields.Selection(O_STATES, readonly=True, default='draft', index=True, string='Estado')

    travel_route_id = fields.Many2one('tms.travel.route', string='Tramo de Viaje', required=True, ondelete='cascade', index=True, copy=False, 
        readonly=True, states={'draft': [('readonly', False)]})
    service_id = fields.Text(compute='_compute_get_service', string='Orden Servicio', store=True)
    customer_id = fields.Text(compute='_compute_get_customer', string='Cliente', store=True)
    load_type_id = fields.Text(compute='_compute_get_loadtype', string='Tipo de Mercadería', store=True)
    #nbr guide se usaba para traer nro guia desde el SOL
    nbr_guide = fields.Text(string='Guias')

    travel_id = fields.Many2one(related="travel_route_id.travel_id", string='Viaje', readonly=True, store=True)
    travel_order = fields.Char(related="travel_id.travel_order", string='OV', readonly=True, store=True)
    travel_date_start = fields.Datetime(related="travel_id.date_start", string='Fecha de Viaje', readonly=True, store=True)
    travel_start_short = fields.Date(string='Fecha corta de Viaje', compute='_compute_get_travel_start_short', store=True)
    travel_state =  fields.Selection(T_STATES, readonly=True, String='Estado Viaje', index=True, related="travel_id.state", store=True)
    travel_operative = fields.Many2one(related="travel_id.employee_operative", string='Coordinador', readonly=True, store=True)
    travel_route_departure = fields.Many2one(related="travel_route_id.departure_id", string="Origen", readonly=True, store=True)
    travel_route_arrival = fields.Many2one(related="travel_route_id.arrival_id", string="Destino", readonly=True, store=True)

    vehicle_id = fields.Many2one('fleet.vehicle', string='Vehículo', domain=[('unit_complement', '=', False)], 
        readonly=True, states={'draft': [('readonly', False)]})
    license_plate = fields.Char(related="vehicle_id.license_plate", string='Tracto', store=True, readonly=True)
    vehicle_outsourcing= fields.Boolean(string='Tercerizado?', readonly=True, help='Indica si el vehículo es Tercerizado')
    vehicle_type_id = fields.Many2one(related="vehicle_id.vehicle_type_id", string='Tipo de Vehículo', store=True, readonly=True)
    driver_id = fields.Many2one('hr.employee', string='Conductor', domain=[('driver', '=', True)], 
        readonly=True, states={'draft': [('readonly', False)]})
    #Proveedor del Conductor
    vendor_driver_id = fields.Many2one('res.partner', string='Proveedor del Conductor', store=True)
    driver_license = fields.Char(string='Brevete', store=True)
    days_license_expire = fields.Char(string='Caducidad de Brevete', compute='_compute_license_expire', readonly=True)
    mobile_phone = fields.Char(related="driver_id.mobile_phone", string='Telf. Conductor', store=True, readonly=True)
    second_vehicle = fields.Many2one('fleet.vehicle', string='Carreta', 
        help='Seleccionar solo si es una Unidad Carreta', readonly=True, states={'draft': [('readonly', False)]})
    license_plate_cmpl = fields.Char(related="second_vehicle.license_plate", string='Carreta', store=True, readonly=True)
    #agent_shipment = fields.Char("Despachador", readonly=True, states={'draft': [('readonly', False)], 'planned': [('readonly', False)], 'programmed': [('readonly', False)]})
    agent_shipment = fields.Many2one('hr.employee', string='Despachador', domain=[('is_dispatcher', '=', True)], 
        readonly=True, states={'draft': [('readonly', False)], 'planned': [('readonly', False)], 'programmed': [('readonly', False)]})
    #Plataforma de vehiculo, propio gps
    platform_gps_1 = fields.Many2one(related="vehicle_id.platform_gps_id", string='Plataforma GPS del Vehículo', store=True, readonly=True, 
        states={'draft': [('readonly', False)], 'planned': [('readonly', False)], 'programmed': [('readonly', False)], 'started': [('readonly', False)]})
    user_gps_1 = fields.Char(string="Usuario GPS", readonly=True, 
        states={'draft': [('readonly', False)], 'planned': [('readonly', False)], 'programmed': [('readonly', False)], 'started': [('readonly', False)]})
    pwd_gps_1 = fields.Char(string="Password GPS", readonly=True, 
        states={'draft': [('readonly', False)], 'planned': [('readonly', False)], 'programmed': [('readonly', False)], 'started': [('readonly', False)]})
    #Plataforma de carreta
    platform_gps_2 = fields.Many2one(related="second_vehicle.platform_gps_id", string='Plataforma GPS de la Carreta', store=True, readonly=True, 
        states={'draft': [('readonly', False)], 'planned': [('readonly', False)], 'programmed': [('readonly', False)], 'started': [('readonly', False)]})
    user_gps_2 = fields.Char(string="Usuario GPS", readonly=True, 
        states={'draft': [('readonly', False)], 'planned': [('readonly', False)], 'programmed': [('readonly', False)], 'started': [('readonly', False)]})
    pwd_gps_2 = fields.Char(string="Password GPS", readonly=True, 
        states={'draft': [('readonly', False)], 'planned': [('readonly', False)], 'programmed': [('readonly', False)], 'started': [('readonly', False)]})
    #Plataforma propia
    device_gps_id = fields.Many2one('tms.gps', string='Dispositivo GPS Propio', readonly=True,
        states={'draft': [('readonly', False)], 'planned': [('readonly', False)], 'programmed': [('readonly', False)], 'started': [('readonly', False)]})
    platform_gps_3 = fields.Char(related="device_gps_id.platform_gps", string='Plataforma GPS Propia', store=True, readonly=True,
        states={'draft': [('readonly', False)], 'planned': [('readonly', False)], 'programmed': [('readonly', False)], 'started': [('readonly', False)]})
    user_gps_3 = fields.Char(related="device_gps_id.user_name", string="Usuario GPS", store=True, readonly=True, 
        states={'draft': [('readonly', False)], 'planned': [('readonly', False)], 'programmed': [('readonly', False)], 'started': [('readonly', False)]})
    pwd_gps_3 = fields.Char(related="device_gps_id.password", string="Password GPS", store=True, readonly=True, 
        states={'draft': [('readonly', False)], 'planned': [('readonly', False)], 'programmed': [('readonly', False)], 'started': [('readonly', False)]})
    #gps_1 =  fields.Char("GPS1", readonly=True, states={'draft': [('readonly', False)], 'planned': [('readonly', False)], 'programmed': [('readonly', False)]})
    #gps_2 =  fields.Char("GPS2", readonly=True, states={'draft': [('readonly', False)], 'planned': [('readonly', False)], 'programmed': [('readonly', False)]})
    #gps_3 =  fields.Char("GPS3", readonly=True, states={'draft': [('readonly', False)], 'planned': [('readonly', False)], 'programmed': [('readonly', False)]})
    vendor_id = fields.Many2one('res.partner', string='Proveedor',  
        readonly=True, states={'draft': [('readonly', False)]})
    vendor_type = fields.Char(string="Tipo Proveedor", compute='_compute_get_vendortype', store=True)
    #vendor_contact = fields.Text(string="Contacto Proveedor", compute='_compute_get_contact', store=True)
    vendor_contact = fields.Many2one('res.partner', string="Contacto Proveedor", readonly=True, states={'draft': [('readonly', False)]})
    vendor_contact_short = fields.Char(related="vendor_contact.name", string='Contacto Proveedor', store=True, readonly=True)
    vendor_contact_phone = fields.Text(string="Telf Contacto", compute='_compute_get_telfcontact', store=True)
    currency_id = fields.Many2one('res.currency', 'Moneda', required=True, readonly=True,
        states={'draft': [('readonly', False)]}, default=lambda self: self.env.user.company_id.currency_id)
    product_id = fields.Many2one('product.product', string='Servicio', 
        readonly=True, states={'draft': [('readonly', False)]})
    cost_ppto_unit = fields.Float(string='Costo Ppto Unitario', default=0.0, readonly=True, 
        states={'draft': [('readonly', False)], 'planned': [('readonly', False)], 'programmed': [('readonly', False)]})
    cost_ppto_unit_hist = fields.Float(string='Costo Ppto Unitario historial', compute='_amount_cost_hist', store=True)
    cost_impt = fields.Float(string='Costo Imputado', compute='amount_all_invoice', store=True)
    cost_vigt = fields.Float(string='Costo Vigente', default=0.0, readonly=True,
        compute='_compute_cost_vigt', store=True)
    check_impt = fields.Boolean(String='Imputado', default=False, readonly=True,
        help="Indica que el Servicio ha sido imputado\n Solo el usuario permitido podrá editarlo.")
    cost_ppto_cpy = fields.Float(string='Subtotal Company', compute='amount_subtotal_total_company', store=True)
    cost_impt_cpy = fields.Float(string='Costo Imputado Company', compute='_find_cost_impt_company', store=True)
    cost_vigt_cpy = fields.Float(string='Costo Vigente Company', compute='_find_cost_vigt_company', store=True)

    product_qty = fields.Float(string='Cantidad', default=1.0, digits='Product Unit of Measure',
        readonly=True, states={'draft': [('readonly', False)]})
    cost_ppto_total = fields.Float(string="Subtotal Ppto", compute='_compute_cost_ppto_total', store=True)
    date_start = fields.Datetime(string='Fecha Ini Planeado', readonly=True,  states={'draft': [('readonly', False)], 'planned': [('readonly', False)]})
    date_start_short = fields.Date(string='Fecha corta Ini Planeado', compute='_compute_get_date_start_short', store=True)
    date_end= fields.Datetime(string='Fecha Fin Planeado', readonly=True,  states={'draft': [('readonly', False)], 'planned': [('readonly', False)]})
    date_start_real = fields.Datetime(string='Fecha Ini Real', readonly=True, states={'programmed': [('readonly', False)]})
    date_end_real= fields.Datetime(string='Fecha Fin Real', readonly=True, states={'started': [('readonly', False)]})
    notes = fields.Text("Notas", readonly=True, states={'draft': [('readonly', False)], 'started': [('readonly', False)]})
    guide_cpy = fields.Char(string='Guia(s) de Empresa')
    guide_customer = fields.Char(string='Guia(s) de Cliente')
    guide_cpy_receive = fields.Boolean(string='Guia(s) Recibida(s)', readonly=False, 
        help="Check si la(s) Guia(s) han sido recibidas\n Solo el usuario permitido podrá editarlo.")
    able_guide_cpy_receive = fields.Boolean(compute='set_access_guide_cpy_receive', string='Usuario puede modificar Recibo de Guias?')
    #Obtener Seguimiento
    #date_track se llena desde la tabla: tms_tracking
    date_track = fields.Datetime(string='Fecha Hora Reg Track')
    date_tracking = fields.Datetime(string='Fecha y Hora Track', compute='_compute_get_date_track')
    type_tracking = fields.Selection(
        [('tracking', 'Seguimiento'),
         ('incidence', 'Incidencia')], string='Tipo Track', compute='_compute_get_date_track')
    status_tracking = fields.Many2one('tms.status.track', string='Estado Track', compute='_compute_get_date_track')
    notes_tracking = fields.Text(string='Observación', compute='_compute_get_date_track')
    track_count = fields.Integer(string='conteo Track', compute='_tracking_count', copy=False)
    track_ids = fields.One2many('tms.tracking', 'route_operation_id')
    #Estados del viaje
    travel_in_planning = fields.Boolean(string='Viaje En Planificación', compute='_compute_change_state01', store=True, default=False)
    travel_in_programming = fields.Boolean(string='Viaje En Programación', compute='_compute_change_state01', store=True, default=False)
    travel_to_start_operation = fields.Boolean(string='Viaje Iniciar Operación', compute='_compute_change_state01', store=True, default=False)
    oper_create_date = fields.Datetime('Fecha de registro', default=(fields.Datetime.now), readonly=True)
    traffic_light = fields.Char(string='Alerta',default='#FFFFFF')
    date_cancel = fields.Datetime(string='Fecha Cancelación', readonly=True)
    invoice_line_ids = fields.One2many('account.move.line', 'route_operation_id', string='Comprobantes Proveedor', domain=[('move_id.move_type', 'in', ('in_invoice','in_refund'))], copy=True, auto_join=True)
    able_modify_check_impt = fields.Boolean(compute='set_access_check_impt', string='Usuario puede modificar Cierre Imputación?')
    advance_ids = fields.One2many('tms.advance', 'route_operation_id', 'Adelanto Proveedor', ondelete='cascade', copy=False)
    #Este campo es actualizado desde tms_advance
    able_advance = fields.Boolean(string='Tiene Adelanto?', readonly=True)
    percent_max_advance = fields.Float(string='Porcentaje Max Adelanto', default=50, readonly=True, states={'draft': [('readonly', False)]})
    able_prctg_max_advance = fields.Boolean(compute='set_access_percent_advance', string='Usuario puede modificar Porcentaje Adelanto?')
    #Se agrega Impuestos y costo ppto total con impuestos
    taxes_id = fields.Many2many('account.tax', string='Impuestos', domain=['|', ('active', '=', False), ('active', '=', True)])
    cost_tax = fields.Float(compute='_compute_cost_ppto_total', string='Costo Impuestos', store=True)
    cost_amount_total = fields.Monetary(compute='_compute_cost_ppto_total', string='Total Ppto', store=True)
    cost_amount_total_company = fields.Float(string='Total Company', compute='amount_subtotal_total_company', store=True)
    #Permitir agregar Adelanto
    allow_advance = fields.Boolean(string='Permitir Adelanto?', default=True, readonly=True)
    guide_receive_date = fields.Date(string='Fecha de Recibo', help="Fecha del recibo de guías")
    vehicle_required = fields.Boolean(related="operation_type.vehicle_required", string='Requiere Vehículo', readonly=True, store=True)
    #Permitir Activar Requerir Guias
    guide_required = fields.Boolean(related="operation_type.guide_required", string='Requiere Guía(s)', readonly=True, store=True)
    justify_overcost_id = fields.Many2one('tms.justify.overcost', string="Justificación de Sobrecosto")
    #Mostrar Adelanto
    show_advance = fields.Boolean(string='Mostrar Adelanto', readonly=True)
    #Se Agrega Nombre Cuenta GPS 1
    name_user_gps_1 = fields.Char(string="Cuenta GPS", readonly=True, 
        states={'draft': [('readonly', False)], 'planned': [('readonly', False)], 'programmed': [('readonly', False)], 'started': [('readonly', False)]})


    #Unicidad de OP
    _sql_constraints = [('operation_name_unique', 'unique(name)', 'La Operación con el mismo Nro OP ya existe')]


    @api.depends('invoice_line_ids.price_subtotal', 'invoice_line_ids.parent_state', 'invoice_line_ids')
    def amount_all_invoice(self):
        #Obtener el monto imputado en Invoices
        for rec_op in self:
            amount_invoice = 0.0
            for line in rec_op.invoice_line_ids:
                if line.parent_state not in ('cancel'): #Solo no permitir anulados
                    if line.move_id.move_type == 'in_refund':
                        amount_invoice = amount_invoice - line.price_subtotal
                    else:
                        amount_invoice = amount_invoice + line.price_subtotal
            self.cost_impt = amount_invoice

    #Obtener el Subtotal y Total Company
    @api.depends('cost_amount_total','cost_ppto_total')
    def amount_subtotal_total_company(self):
        for op1 in self:
            if op1.currency_id == op1.company_id.currency_id:
                v_cost_amount_total_company = op1.cost_amount_total
                v_cost_ppto_cpy = op1.cost_ppto_total
            else:
                v_cost_amount_total_company = self.env['res.currency']._compute(op1.currency_id, op1.company_id.currency_id, op1.cost_amount_total)
                v_cost_ppto_cpy = self.env['res.currency']._compute(op1.currency_id, op1.company_id.currency_id, op1.cost_ppto_total)
            op1.cost_amount_total_company = v_cost_amount_total_company #TOTAL COMPANY
            op1.cost_ppto_cpy = v_cost_ppto_cpy #SUBTOTAL COMPANY

    @api.onchange('product_id')
    def onchange_product_id(self):
        self._compute_taxes_id()
        self.cost_ppto_unit = self.product_id.standard_price
        self.currency_id = self.product_id.currency_id

    #=================== INI IMPUESTOS Y TOTALES =======================
    @api.depends('product_qty', 'cost_ppto_unit', 'taxes_id')
    def _compute_cost_ppto_total(self):
        for rec in self:
            if rec.vendor_required == True:
                taxes = rec.taxes_id.compute_all(rec.cost_ppto_unit, rec.currency_id, rec.product_qty, product=rec.product_id, partner=rec.vendor_id)
                rec.update({
                    'cost_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                    'cost_amount_total': taxes['total_included'],
                    'cost_ppto_total': taxes['total_excluded'],
                })
            else:
                v_cost_ppto_total = 0
                v_cost_ppto_total = rec.cost_ppto_unit * rec.product_qty
                rec.update({
                    'cost_tax': 0,
                    'cost_amount_total': v_cost_ppto_total,
                    'cost_ppto_total': v_cost_ppto_total,
                })

    def _compute_taxes_id(self):
        for line in self:
            if line.vendor_required == True:
                fpos = line.vendor_id.property_account_position_id
                taxes = line.product_id.supplier_taxes_id.filtered(lambda r: not line.company_id or r.company_id == line.company_id)
                line.taxes_id = fpos.map_tax(taxes, line.product_id, line.vendor_id) if fpos else taxes

    @api.depends('currency_id')
    def _amount_cost_hist(self):
        for rec in self:
            if rec.currency_id == rec.company_id.currency_id:
                v_costo_hist = rec.product_id.standard_price
            else:
                v_costo_hist = self.env['res.currency']._compute(rec.company_id.currency_id, rec.currency_id, rec.product_id.standard_price)

            rec.update({
                'cost_ppto_unit_hist': v_costo_hist,
            })

    #=================== FIN IMPUESTOS Y TOTALES =======================

    #Obtener el Costo Vigente Company
    @api.depends('cost_vigt', 'currency_id')
    def _find_cost_vigt_company(self):
        for vigt3 in self:
            if vigt3.currency_id == vigt3.company_id.currency_id:
                v_cost_vigt_cpy = vigt3.cost_vigt
            else:
                v_cost_vigt_cpy = self.env['res.currency']._compute(vigt3.currency_id, vigt3.company_id.currency_id, vigt3.cost_vigt)
            vigt3.cost_vigt_cpy = v_cost_vigt_cpy

    #Obtener el Costo Imputado Company
    @api.depends('cost_impt', 'currency_id')
    def _find_cost_impt_company(self):
        for impt2 in self:
            if impt2.currency_id == impt2.company_id.currency_id:
                v_cost_impt_cpy = impt2.cost_impt
            else:
                v_cost_impt_cpy = self.env['res.currency']._compute(impt2.currency_id, impt2.company_id.currency_id, impt2.cost_impt)
            impt2.cost_impt_cpy = v_cost_impt_cpy

    def set_access_percent_advance(self):
        self.able_prctg_max_advance = self.env['res.users'].has_group('tms.group_allow_change_percentage_advance')

    def set_access_guide_cpy_receive(self):
        self.able_guide_cpy_receive = self.env['res.users'].has_group('tms.group_allow_guide_cpy_receive')

    def set_access_check_impt(self):
        self.able_modify_check_impt = self.env['res.users'].has_group('tms.group_allow_lock_imputation_services')

    #========================= INI BUSCAR TRACKING =========================
    def _tracking_count(self):
        tracking_ids = self.env['tms.tracking'].search([('route_operation_id', '=', self.id)])
        self.track_count = len(tracking_ids)

    def action_view_tracking(self):
        trk_obj = self.env['tms.tracking'].search([('route_operation_id', '=', self.id)])
        trk_ids = []
        for each in trk_obj:
            trk_ids.append(each.id)
        view_id = self.env.ref('tms.open_view_tms_tracking_form').id

        if trk_ids:
            if len(trk_ids) < 1:
                value = {
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'tms.tracking',
                    'view_id': view_id,
                    'type': 'ir.actions.act_window',
                    'name': 'Seguimiento',
                    'res_id': trk_ids and trk_ids[0]
                }
            else:
                value = {
                    'domain': str([('id', 'in', trk_ids)]),
                    'view_type': 'form',
                    'view_mode': 'tree,form',
                    'res_model': 'tms.tracking',
                    'view_id': False,
                    'type': 'ir.actions.act_window',
                    'name': 'Seguimiento',
                    'res_id': trk_ids
                }

            return value
    #========================= FIN BUSCAR TRACKING =========================

    @api.depends('state')
    def _compute_change_state01(self):
        #Si al menos 01 Operacion del Viaje esta en estado "Borrador"
        d_state_01 = self.env['tms.route.operation'].search([('travel_id','=', self.travel_id.id), ('state','=', 'draft')], limit=1)
        if d_state_01:
            #Obtener mediante query
            query = """UPDATE tms_route_operation set travel_in_planning = True 
                    where """
            query += " travel_id = %s " % (self.travel_id.id)
            query += " "
            self.env.cr.execute(query)
            self.travel_in_planning = True
        else:
            #Obtener mediante query
            query = """UPDATE tms_route_operation set travel_in_planning = False 
                    where """
            query += " travel_id = %s " % (self.travel_id.id)
            query += " "
            self.env.cr.execute(query)
            self.travel_in_planning = False

        #Si al menos 01 Operacion del Viaje esta en estado "Planificado"
        d_state_02 = self.env['tms.route.operation'].search([('travel_id','=', self.travel_id.id), ('state','=', 'planned')], limit=1)
        if d_state_02:
            #Obtener mediante query
            query2 = """UPDATE tms_route_operation set travel_in_programming = True 
                    where """
            query2 += " travel_id = %s " % (self.travel_id.id)
            query2 += " "
            self.env.cr.execute(query2)
            self.travel_in_programming = True
        else:
            #Obtener mediante query
            query2 = """UPDATE tms_route_operation set travel_in_programming = False 
                    where """
            query2 += " travel_id = %s " % (self.travel_id.id)
            query2 += " "
            self.env.cr.execute(query2)
            self.travel_in_programming = False

        #Si al menos 01 Operacion del Viaje esta en estado "Programado"
        d_state_03 = self.env['tms.route.operation'].search([('travel_id','=', self.travel_id.id), ('state','=', 'programmed')], limit=1)
        if d_state_03:
            #Obtener mediante query
            query3 = """UPDATE tms_route_operation set travel_to_start_operation = True 
                    where """
            query3 += " travel_id = %s " % (self.travel_id.id)
            query3 += " "
            self.env.cr.execute(query3)
            self.travel_to_start_operation = True
        else:
            #Obtener mediante query
            query3 = """UPDATE tms_route_operation set travel_to_start_operation = False 
                    where """
            query3 += " travel_id = %s " % (self.travel_id.id)
            query3 += " "
            self.env.cr.execute(query3)
            self.travel_to_start_operation = False

    #Obtener fecha corta del viaje
    @api.depends('travel_id.date_start')
    def _compute_get_travel_start_short(self):
        if self.travel_id.date_start:
            self.travel_start_short = self.travel_id.date_start
        else:
            self.travel_start_short = False

    #Obtener fecha corta inicio planeado
    @api.depends('date_start')
    def _compute_get_date_start_short(self):
        if self.date_start:
            self.date_start_short = self.date_start
        else:
            self.date_start_short = False

    #Obtener servicios asociados al Tramo
    @api.depends('travel_route_id.travel_route_service_ids')
    def _compute_get_service(self):
        v_service = ''
        v_len = 0
        #Obtener mediante query
        query = """SELECT d.name
                    FROM tms_travel_route_service b, sale_order_line c, sale_order d
                    where c.id = b.sale_order_line_id
                    and d.id = c.order_id"""
        query += " and b.travel_route_id = %s " % (self.travel_route_id.id)
        query += "  group by d.name"
        self.env.cr.execute(query)
        data_service = self.env.cr.fetchall() or False

        if data_service:
            for line in data_service:
                v_service += ''.join([str(col) for col in line]) + ', '
            
            v_len = len(v_service)
            if v_len > 1:
                v_len = v_len - 2
                v_service = v_service[0:v_len]

        self.service_id = v_service

    #Obtener clientes asociados al servicio del Tramo
    @api.depends('travel_route_id.travel_route_service_ids')
    def _compute_get_customer(self):
        v_customer = ''
        v_len = 0
        #Obtener mediante query
        query = """SELECT d.name
                    FROM tms_travel_route_service b, sale_order_line c, res_partner d
                    where c.id = b.sale_order_line_id
                    and d.id = c.order_partner_id"""
        query += " and b.travel_route_id = %s " % (self.travel_route_id.id)
        query += "  group by d.name"
        self.env.cr.execute(query)
        data_customer = self.env.cr.fetchall() or False

        if data_customer:
            for line in data_customer:
                v_customer += ''.join([str(col) for col in line]) + ', '
            
            v_len = len(v_customer)
            if v_len > 1:
                v_len = v_len - 2
                v_customer = v_customer[0:v_len]
        self.customer_id = v_customer

    #Obtener tipo de mercaderia asociados al servicio del Tramo
    @api.depends('travel_route_id.travel_route_service_ids')
    def _compute_get_loadtype(self):
        v_merchtype = ''
        v_len = 0
        #Obtener mediante query
        query = """SELECT d.name
                    FROM tms_travel_route_service b, sale_order_line c, tms_load_type d
                    where c.id = b.sale_order_line_id
                    and d.id = c.load_type_id"""
        query += " and b.travel_route_id = %s " % (self.travel_route_id.id)

        query += "  group by d.name"

        self.env.cr.execute(query)
        data_merchtype = self.env.cr.fetchall() or False

        if data_merchtype:
            for line in data_merchtype:
                v_merchtype += ''.join([str(col) for col in line]) + ', '
            
            v_len = len(v_merchtype)
            if v_len > 1:
                v_len = v_len - 2
                v_merchtype = v_merchtype[0:v_len]
        self.load_type_id = v_merchtype

    #Creacion con el correlativo de la Operacion
    @api.model
    def create(self, vals):        
        if vals.get('name','Nuevo') == 'Nuevo':
            if 'company_id' in vals and vals['company_id']:
                vals['name'] = self.env['ir.sequence'].with_context(force_company=vals['company_id']).next_by_code('tms.route.operation') or 'Nuevo'
            else:
                vals['name'] = self.env['ir.sequence'].next_by_code('tms.route.operation') or 'Nuevo'

        result = super(TmsRouteService, self).create(vals)
        return result

    #Obtener los datos del tracking
    def _compute_get_date_track(self):
        for operation in self:
            #v_name = (self.operation_type.id or '')
            #raise ValidationError(_("dato: '%s'.") % (v_name))
            v_date = ''
            v_type = ''
            v_status = ''
            v_obs = ''
            d_tracks = self.env['tms.tracking'].search([('travel_id','=', operation.travel_id.id), ('travel_route_id','=', operation.travel_route_id.id), ('route_operation_id','=', operation.id), ('operation_type_id','=', operation.operation_type.id)], order='date desc', limit=1)

            if d_tracks:
                for records in d_tracks:
                    v_date = (records.date or '')
                    v_type = (records.type_tracking or '')
                    v_status = (records.status_track or '')
                    v_obs = (records.notes or '')

            operation.date_tracking = v_date
            operation.type_tracking = v_type
            operation.notes_tracking = v_obs
            if v_status != '':
                operation.status_tracking = v_status
            else:
                operation.status_tracking = False
            #raise ValidationError(_("dato: '%s'.") % (v_status))

    #Mejora aplicada al check de imputado TH 20OCT2020
    @api.depends('check_impt', 'invoice_line_ids', 'invoice_line_ids.parent_state', 'cost_ppto_unit')
    def _compute_cost_vigt(self):
        for rec in self:
            if rec.check_impt == True:
                #Valida si tiene proveedor
                if rec.vendor_required == True:
                    #Si el proveedor es igual al Company
                    if rec.vendor_id == rec.company_id.partner_id:
                        #rec.cost_vigt = rec.cost_ppto_total + rec.cost_impt
                        #Por Def Requerimiento
                        #rec.cost_vigt = rec.cost_impt
                        #Por Def JA y ACarlin 02DIC2020
                        rec.cost_vigt = rec.cost_ppto_total
                    else:
                        rec.cost_vigt = rec.cost_impt
                else:
                    rec.cost_vigt = rec.cost_impt
            else:
                rec.cost_vigt = rec.cost_ppto_total

    @api.onchange('vehicle_id')
    def onchange_vehicle_id(self):
        if self.vendor_required == True:
            self.vendor_id = self.vehicle_id.partner_id
        self.driver_id = self.vehicle_id.employee_driver_id
        self.vehicle_outsourcing = self.vehicle_id.outsourcing

    @api.onchange('driver_id')
    def onchange_driver_id(self):
        for rec in self:
            if rec.driver_id:
                if rec.driver_id.is_blacklist_driver == True:
                    raise UserError(_(
                            "ALERTA :: CONDUCTOR EN LISTA NEGRA! \n \n"
                            "Conductor: '%s' \n"
                            "Motivo: \n"
                            "%s \n \n"
                            "Se recomienda convocar a otro conductor \n"
                            "Consulte con su Supervisor para eliminar este mensaje.") % (
                            self.driver_id.name, self.driver_id.reason_blacklist))
                else:
                    rec.vendor_driver_id = rec.driver_id.partner_id
                    rec.driver_license = rec.driver_id.driver_license

    @api.depends('driver_id')
    def _compute_license_expire(self):
        for rec in self:
            # Ini caducidad de Licencia
            now = fields.Datetime.now()
            date_expire = rec.driver_id.license_expiration if rec.driver_id.license_expiration else fields.Datetime.now()
            delta = date_expire - now
            if delta.days >= -1:
                v_count_date = delta.days + 1
            else:
                v_count_date = 0
            rec.days_license_expire = str(v_count_date)  + '  dia(s)'
            # Fin caducidad de Licencia

    #Modificado
    @api.depends('vendor_contact')
    def _compute_get_telfcontact(self):
        v_name = ''
        if self.vendor_contact.id:
            for records in self.env['res.partner'].search([('id', '=', self.vendor_contact.id),('parent_id', '!=',None),('type','=','contact')]):
                if records.mobile:
                    v_name = (records.mobile or '')

            self.vendor_contact_phone = v_name

    #Modificado
    @api.depends('vendor_id')
    def _compute_get_vendortype(self):
        v_tipo = None
        self.vendor_type = v_tipo
        if self.vendor_id.id:
            for records in self.env['res.company'].search([('id', '=', self.company_id.id)]):
                if self.vendor_id.id == records.partner_id.id:
                    v_tipo = 'propio'
                else:
                    v_tipo = 'tercero'
            self.vendor_type = v_tipo
            #v_name = self.vendor_id.id
            reg_vendor = self.env['res.partner.alerts'].search([
                ('partner_id','=', self.vendor_id.id), ('group_alert','=', 'operation'),('alert_active','=','activo')])
            if reg_vendor:
                v_msg = ''
                for d_vendor in reg_vendor:
                    v_msg = v_msg + d_vendor.message + "\n"
                    #v_msg = ("Alerta para %s") % self.vendor_id.name
                if len(v_msg) > 1:
                    raise UserError(_(
                        "ALERTA :: PROVEEDOR EN LISTA NEGRA! \n \n"
                        "Proveedor: '%s' \n"
                        "Mensaje: \n"
                        "%s \n \n"
                        "Consulte con su Supervisor para eliminar este mensaje.") % (
                        self.vendor_id.name,
                        v_msg))

    #================================ INI ESTADOS ================================
    #Planificado
    def action_planned(self):
        for rec in self:           
            # --> Si la Operación es Flete
            if rec.operation_type.vehicle_required == True:
                if not rec.vehicle_id:
                    raise UserError(_('Debe ingresar el dato del vehículo!'))
                if not rec.driver_id:
                    raise UserError(_('Debe ingresar el dato del conductor!'))
            if not rec.cost_ppto_unit:
                raise UserError(_('Debe ingresar el costo ppto unitario!'))
            if not rec.product_qty:
                raise UserError(_('Debe ingresar la cantidad!'))
            # --> Si la Operación pasa de Borrador a Planificado, entonces el Viaje tambien se cambia
            if (rec.travel_id and rec.travel_id.state == 'draft'):
                rec.travel_id.state = "planned"
            if (rec.travel_route_id and rec.travel_route_id.state == 'draft'):
                rec.travel_route_id.state = "confirmed"
            rec.state = "planned"

    #Programado
    def action_programmed(self):
        for rec in self:
            if not rec.date_start:
                raise UserError(_('Debe ingresar la Fecha inicio planeado!'))
            if not rec.date_end:
                raise UserError(_('Debe ingresar la Fecha fin planeado!'))
            if (rec.date_start and rec.date_end and rec.date_start > rec.date_end):
                raise UserError(_('La Fecha inicio planeado debe ser menor o igual a la Fecha fin planeado!'))
            #Valida que tenga dato de Orden de Servicio
            if not rec.service_id:
                raise UserError(_("Debe Asociar al menos una Orden de Servicio al Viaje: '%s'.") % (str(rec.travel_id.name)))
            # --> Si la Operación pasa de Planificado a Programado, entonces el Viaje tambien se cambia
            if (rec.travel_id and rec.travel_id.state == 'planned'):
                rec.travel_id.state = "programmed"
            rec.state = "programmed"

    #En curso
    def action_started(self):
        for rec in self:
            if not rec.date_start_real:
                rec.date_start_real = fields.Datetime.now()
            rec.traffic_light = color_green
            rec.state = "started"
            # --> Si la Operación pasa de Programado a En Curso, entonces el Viaje tambien se cambia
            if (rec.travel_id and rec.travel_id.state == 'programmed'):
                rec.travel_id.state = "started"
                rec.travel_id.date_start_real = rec.date_start_real

    #Terminado
    def action_finished(self):
        for rec in self:
            if not rec.date_end_real:
                rec.date_end_real = fields.Datetime.now()
            rec.traffic_light = color_white
            #Cerramos permitir adelantos solo para 3ros. En caso de Propio se cierra con el check de Imputacion 18DIC2020
            if rec.vendor_type == 'tercero':
                rec.allow_advance = False
            rec.state = "finished"

            # --> Si la Operación pasa de En Curso a Terminado y el Viaje esta en estado En Curso, entonces el viaje se pasa a Terminado
            v_dato = True
            reg_travel = self.env['tms.route.operation'].search([('travel_id','=', self.travel_id.id), ('id','!=', self.id), ('state','not in', ('canceled', 'finished') )])
            if reg_travel:
                v_dato = False

            if v_dato == True:
                rec.travel_id.state = "finished"
                if not rec.travel_id.date_end_real:
                    rec.travel_id.date_end_real = rec.date_end_real
                else:
                    if rec.travel_id.date_end_real < rec.date_end_real:
                        rec.travel_id.date_end_real = rec.date_end_real

    #Cancelado
    def action_canceled(self):
        for rec in self:
            # --> Si la Operación esta Terminada y el Viaje Terminado, entonces no se puede cancelar
            if (rec.travel_id and rec.travel_id.state == 'finished' and rec.state == 'finished'):
                raise UserError(_('No puedes Cancelar esta Operación cuando el Viaje está Terminado!'))
            #Si la Operación esta Terminado, no se puede cancelar
            if rec.state == 'finished':
                raise UserError(_('No puedes Cancelar esta Operación cuando está Terminado!'))
            #Buscamos si hay adelantos no cancelados, si lo hubiera no se puede cancelar la Operacion
            advances = rec.advance_ids.search([
                ('state', '!=', 'cancel'),
                ('route_operation_id', '=', rec.id)])
            if len(advances) >= 1:
                raise ValidationError(_('No puede cancelar la Operación! \n Primero debe cancelar el Adelanto.'))
            #Buscamos si hay Comprobante de Proveedor no anulado, si lo hubiera no se puede cancelar la Operacion
            inv_line = rec.invoice_line_ids.search([
                ('parent_state', '!=', 'cancel'),
                ('route_operation_id', '=', rec.id)])
            if len(inv_line) >= 1:
                raise ValidationError(_('No puede cancelar la Operación! \n Primero debe cancelar el Comprobante del Proveedor.'))
            #Cerramos permitir adelantos
            rec.allow_advance = False
            rec.state = "canceled"
            rec.cost_ppto_unit = 0
            rec.cost_ppto_unit_hist = 0
            rec.cost_vigt=0
            rec.cost_vigt_cpy=0
            if not rec.date_cancel:
                rec.date_cancel = fields.Datetime.now()
            rec.traffic_light = color_white
            # --> Si la Operación pasa a Cancelado, entonces el viaje se pasa a Terminado o Cancelado
            v_dato = True
            reg_travel = self.env['tms.route.operation'].search([('travel_id','=', self.travel_id.id), ('id','!=', self.id), ('state','not in', ('canceled', 'finished') )])
            if reg_travel:
                v_dato = False

            if v_dato == True:
                reg_travel2 = self.env['tms.route.operation'].search(
                    [('travel_id','=', self.travel_id.id), ('id','!=', self.id), ('state','=', 'finished')])
                if reg_travel2:
                    rec.travel_id.state = "finished"
                else:
                    rec.travel_id.state = "canceled"

                if not rec.travel_id.date_end_real:
                    rec.travel_id.date_end_real = rec.date_cancel
                else:
                    if rec.travel_id.date_end_real < rec.date_cancel:
                        rec.travel_id.date_end_real = rec.date_cancel

    #================================ FIN ESTADOS ================================

    @api.onchange('operation_type')
    def onchange_operation_type(self):
        #Al resetear el vehiculo, tambien resetea por defecto los demas datos del vehiculo 
        self.vehicle_id = False
        self.second_vehicle = False
        self.allow_advance = self.operation_type.able_advance
        self.show_advance = self.operation_type.able_advance
        self.percent_max_advance = self.operation_type.percent_advance

    def action_tracking_record(self):
        return {
            'name': 'Seguimiento',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'tms.tracking',
            'type': 'ir.actions.act_window',
            'target': 'new'
            }

    def action_view_web_gps1(self):
        self.ensure_one()
        v_url = self.platform_gps_1.name
        if not v_url:
            raise UserError(_("Falta URL del GPS Vehicular para la Operación: '%s'.") % self.name)
        return {
            'type': 'ir.actions.act_url',
            'url': v_url,
            'target': 'new',
            }

    def action_view_web_gps2(self):
        self.ensure_one()
        v_url = self.platform_gps_2.name
        if not v_url:
            raise UserError(_("Falta URL de GPS de la Carreta para la Operación: '%s'.") % self.name)
        return {
            'type': 'ir.actions.act_url',
            'url': v_url,
            'target': 'new',
            }

    def action_view_web_gps3(self):
        self.ensure_one()
        v_url = self.device_gps_id.platform_gps
        if not v_url:
            raise UserError(_("Falta URL de GPS de la Carreta para la Operación: '%s'.") % self.name)
        return {
            'type': 'ir.actions.act_url',
            'url': v_url,
            'target': 'new',
            }


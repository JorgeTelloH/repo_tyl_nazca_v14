
from odoo import api,fields,models,_
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError


class AccountMove(models.Model):
    _inherit = "account.move"

    l10n_pe_withhold = fields.Boolean(
        string="Sujeto a detraccion",
        states={'draft': [('readonly', False)]},
        readonly=True,)

    l10n_pe_withhold_code = fields.Selection(
        selection=[
            ('001', '01 Azúcar y melaza de caña'),
            ('002', '02 Arroz'),
            ('003', '03 Alcohol etílico'),
            ('004', '04 Recursos hidrobiológicos'),
            ('005', '05 Maíz amarillo duro'),
            ('006', '06 Algodón'),
            ('007', '07 Caña de azúcar'),
            ('008', '08 Madera'),
            ('009', '09 Arena y piedra'),
            ('010', '10 Residuos, subproductos, desechos, recortes y desperdicios'),
            ('011', '11 Bienes gravados con el IGV, o renuncia a la exoneración'),
            ('012', '12 Intermediación laboral y tercerización'),
            ('013', '13 Animales vivos'),
            ('014', '14 Carnes y despojos comestibles'),
            ('015', '15 Abonos, cueros y pieles de origen animal'),
            ('016', '16 Aceite de pescado'),
            ('017', '17 Harina, polvo y “pellets” de pescado, crustáceos, moluscos y demás invertebrados acuáticos'),
            ('018', '18 Embarcaciones pesqueras'),
            ('019', '19 Arrendamiento de bienes muebles'),
            ('020', '20 Mantenimiento y reparación de bienes muebles'),
            ('021', '21 Movimiento de carga'),
            ('022', '22 Otros servicios empresariales'),
            ('023', '23 Leche'),
            ('024', '24 Comisión mercantil'),
            ('025', '25 Fabricación de bienes por encargo'),
            ('026', '26 Servicio de transporte de personas'),
            ('027', '27 Servicio de transporte de carga'),
            ('028', '28 Transporte de pasajeros'),
            ('029', '29 Algodón en rama sin desmontar'),
            ('030', '30 Contratos de construcción'),
            ('031', '31 Oro gravado con el IGV'),
            ('032', '32 Páprika y otros frutos de los géneros capsicum o pimienta'),
            ('033', '33 Espárragos'),
            ('034', '34 Minerales metálicos no auríferos'),
            ('035', '35 Bienes exonerados del IGV'),
            ('036', '36 Oro y demás minerales metálicos exonerados del IGV'),
            ('037', '37 Demás servicios gravados con el IGV'),
            ('039', '39 Minerales no metálicos'),
            ('040', '40 Bien inmueble gravado con IGV'),
            ('041', '41 Plomo'),
            ('099', '99 Ley 30737')
        ],
        string="Código Detracción",
        readonly=True,
        states={'draft': [('readonly', False)]},
        help="Catálogo 54 SUNAT, Código de Detracción")

    l10n_pe_withhold_percentage = fields.Float(
        string="Porcentaje Detracción",
        readonly=True,
        states={'draft': [('readonly', False)]},
        help="Porcentaje de Detracción segun RS 183-2004/SUNAT")

    detraction_payer = fields.Selection(
        selection=[('partner', 'Socio'),
                   ('company', 'Empresa')],
        string='Paga Detracción',
        default='partner',
        help='Indica el responsable que realizará el deposito de la Detracción del Comprobante.')

    det_fecpago = fields.Date('Fecha Pago Pago Det.')

    det_nropago = fields.Char('Número Pago Det.', size=15,
                              help="Para registrar el Nro. de Comprobante de Pago de Detracción")

    @api.onchange('invoice_line_ids')
    def _onchange_invoice_line_ids2(self):
        if self.invoice_line_ids:
            obj_spot = False
            list_prodc = [line.product_id for line in self.invoice_line_ids if line.product_id.id]
            if list_prodc:
                obj_spot = self._l10n_pe_edi_get_spot()
            if obj_spot:
                self.l10n_pe_withhold = True
                self.l10n_pe_withhold_code = obj_spot.get('PaymentMeansID')
                self.l10n_pe_withhold_percentage = obj_spot.get('PaymentPercent')
            else:
                self.l10n_pe_withhold = False
                self.l10n_pe_withhold_code = False
                self.l10n_pe_withhold_percentage = False


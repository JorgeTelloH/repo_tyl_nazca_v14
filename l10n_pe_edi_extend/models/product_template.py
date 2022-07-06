# -*- coding: utf-8 -*-
from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

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
        string="Withhold code",
        help="Catalog No. 54 SUNAT, used functionally to document in the printed document on invoices that need to "
             "have the proper SPOT text")


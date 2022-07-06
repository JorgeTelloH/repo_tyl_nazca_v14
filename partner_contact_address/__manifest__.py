# -*- coding: utf-8 -*-
{
    'name': 'Direccion Delivery y Facturación del socio',
    'summary': 'Direccion Delivery y Facturación predeterminada del socio',
    'description': """
        Permitir configurar la de Direccion de Delivery y Facturación en el modulo de Contactos.
    """,
    'author': 'TH',
    'website': 'http://www.cabalcon.com',
    
    'category': 'Sales/CRM',
    'version': '1.1',
    
    # any module necessary for this one to work correctly
    'depends': ['contacts'],

    # always loaded
    'data': [
    	'views/res_partner_view.xml',
    ],
}

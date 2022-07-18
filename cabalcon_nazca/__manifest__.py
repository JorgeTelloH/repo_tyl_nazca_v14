# -*- encoding: utf-8 -*-

{
    'name': 'Modulo de transporte Nazca',
    'summary': """
    	Transporte Nazca
    """,
    'version': '14.0',
    'category': 'otros',
    'description': """

    """,
    'author': 'Oswaldo Lopez (Cabalcon)',
    'website': 'www.cabalcon.com',
    'depends': ['contacts','l10n_latam_base','l10n_pe','kw_address_gmap_link','tms','hide_menu_submenu_reports','fleet'],
    'data': [
        'data/data.xml',
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/tms_tracking.xml',
        'views/menu.xml',
        'views/partner.xml',
        'views/fleet.xml',
        'views/operations.xml',
        'views/documents.xml',
        'views/booking.xml',
        'views/address_views.xml',
        'views/ship.xml',
        'views/operation_type.xml',
        'views/travel_route.xml',


    ],
}


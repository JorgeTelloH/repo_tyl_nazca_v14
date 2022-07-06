# -*- coding: utf-8 -*-
{
    'name': "Administración de Transportes",

    'summary': """
        Gestión de Transportes Propio y Tercero""",

    'description': """
        Administración Operativa de Transportes Propio y Tercero.""",

    'author': "TH - Oswaldo Lopez",
    'website': "http://www.cabalcon.com.pe",

    'category': 'Transport',
    'version': '1.1',

    # any module necessary for this one to work correctly
    'depends': ['base','fleet','sale','hr','contacts','add_sale_operations',
                'sh_message','l10n_pe_edi','partner_account_banks','account_fleet',
                'fleet_vehicle_type','add_fleet_driver'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'wizard/multiple_sol_travel_view.xml',
        'views/tms_view.xml',
        'views/tms_route_operation_view.xml',
        'views/tms_travel_route_view.xml',
        'views/tms_travel_view.xml',
        'views/account_payment_view.xml',
        'views/tms_tracking_view.xml',
        'views/tms_route_operation_type_view.xml',
        'views/fleet_vehicle_view.xml',
        'views/tms_gps_view.xml',
        'views/tms_place_view.xml',
        'views/sale_line_view.xml',
        'views/sale_order_line_view.xml',
        'views/product_template_view.xml',
        'views/res_partner_view.xml',
        'views/tms_status_track_view.xml',
        'views/fleet_vehicle_capacity_view.xml',
        'views/tms_load_type_view.xml',
        'views/tms_loan_gps_view.xml',
        'views/tms_alarm_email_view.xml',
        'views/tms_justify_overcost_view.xml',


    ],

}
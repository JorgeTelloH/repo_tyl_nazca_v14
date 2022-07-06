# -*- coding: utf-8 -*-

{
    'name': 'Operations Delivery Extend',
    'depends': ['operation_production', 'cabalcon_hr_payroll'],
    'description': """
		Human resource operaciones de Delivery
    """,
    'category': 'Operations',
    'data': [
        'security/ir.model.access.csv',
        'data/hr_salary_rule_data.xml',
        'views/calender_driver.xml',
        'views/roll_views.xml',
        'views/operations_view.xml',
        'views/res_location_view.xml',
    ],
    'qweb': [],
    'application': False,
    'auto_install': False
}

# -*- coding: utf-8 -*-

{
    'name': 'Comisiones por ventas',
    'version': '1.0',
    'author': "Cabalcon",
    'website': "www.cabalcon.com",
    'category': 'Accounting/Accounting',
    'summary': 'Administra las comisiones por ventas para los empleados.',
    'depends': ['account', 'cabalcon_hr_payroll'],
    'data': [
        'security/ir.model.access.csv',
        'data/salary_rule_commission.xml',
        'views/account_sale_commission_views.xml',
        'views/hr_payslip_views.xml',
    ],
    'installable': True,
    'application': False,
}

# -*- coding: utf-8 -*-
{
    'name': 'Employee fifth category',
    'version': '14.0.1.0.0',
    'summary': """Calculo de la renta de quinta categoría""",
    'description': 'Este módulo lo ayuda a calcular a renta de quinta categoría de los empleados.',
    'category': 'Generic Modules/Human Resources',
    'author': 'Cabalcon',
    'website': "www.cabalcon.com",
    'depends': ['cabalcon_hr_payroll'],
    'data': [
        'security/ir.model.access.csv',
        'data/tax_data.xml',
        'views/hr_employee_view.xml',
        'views/hr_fifth_category.xml',
        # 'views/hr_payslip_run.xml',
        'reports/report_5th_category_rent.xml',

    ],
    
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}

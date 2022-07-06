# -*- coding: utf-8 -*-
{
    'name': 'Employee Family Info',
    'version': '14.0.1.0.0',
    'summary': """información sobre la familia del empleado""",
    'description': 'Este módulo lo ayuda a agregar información sobre la familia del empleado.',
    'category': 'Generic Modules/Human Resources',
    'author': 'Cabalcon',
    'website': "www.cabalcon.com",
    'depends': ['base', 'cabalcon_hr'],
    'data': [
        'security/ir.model.access.csv',
        'data/data.xml',
        'views/hr_employee_view.xml',
        'views/employee_family.xml',

    ],
    'images': ['static/description/banner.png'],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}

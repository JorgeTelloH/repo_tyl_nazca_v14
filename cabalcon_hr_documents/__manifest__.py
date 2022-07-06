# -*- coding: utf-8 -*-

{
    'name': 'Employee Documents',
    'version': '14.0.1.0.0',
    'summary': """Manages Employee Documents""",
    'description': """Manages Employee Related Documents""",
    'category': 'Generic Modules/Human Resources',
    'author': 'Cabalcon',
    'company': 'Cabalcon',
    'maintainer': 'Cabalcon',
    'website': "www.cabalcon.com",
    'depends': ['base', 'cabalcon_hr'],
    'data': [
        'security/ir.model.access.csv',
        'data/demo_data.xml',
        'views/employee_document_view.xml',
     
    ],
    'demo': [],
    'images': ['static/description/banner.png'],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}

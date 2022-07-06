# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Cabalcon Online Jobs',
    'category': 'Website/Website',
    'sequence': 310,
    'version': '14.0.1.0.0',
    'summary': 'Manage your online hiring process',
    'description': "This module allows to publish your available job positions on your website and keep track of application submissions easily. It comes as an add-on of *Recruitment* app.",
    'author': "Cabalcon",
    'website': "www.cabalcon.com",
    'depends': ['cabalcon_hr_recruitment', 'website_hr_recruitment'],
    'data': [
        'security/ir.model.access.csv',
        'data/config_data.xml',
        'views/website_hr_recruitment_templates.xml',
        # 'views/hr_recruitment_views.xml',
        # 'views/hr_job_views.xml',
    ],
    'demo': [
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}

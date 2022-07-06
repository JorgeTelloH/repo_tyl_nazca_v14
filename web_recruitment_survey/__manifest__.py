# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Survey recruitment',
    'version': '1.0',
    "author": "Cabalcon",
    'website': '',
    'category': 'Web',
    'summary': 'Survey recruitment',
    'description': """
    Survey

    """,
    'depends': [
                'website_hr_recruitment',
                ],
    'data': [
        'views/recruitment_survey_template.xml',
        'views/assets.xml'
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}

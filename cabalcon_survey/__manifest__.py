# -*- encoding: utf-8 -*-

{
    'name': 'Surveys',
    'version': '1.0',
    'category': 'Marketing/Surveys',
    'description': """Agregar un campo categoría para que las encuestas estén clasificadas según el proceso""",
    'summary': 'Clasificar la encuesta según el proceso',
    'website': 'www.cabalcon.com',
    'depends': [
        'survey', 'report_xlsx'
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/survey_category_data.xml',
        'views/survey_survey_views.xml',
        'views/survey_category_views.xml',
        'wizard/survey_export_wizard_view.xml',
    ],
   
    'installable': True,
    'auto_install': False,
    'application': False,
    'sequence': 220,
    'license': 'LGPL-3',
}

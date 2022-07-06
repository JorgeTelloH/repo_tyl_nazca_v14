# -*- encoding: utf-8 -*-

{
    'name': 'Survey Attachment',
    'summary': """
        An easy way to attach a file to your survey. This functionality is realized through choosing the type of questions beforehand; then uploading the file.""",
    'version': '12.0',
    'category': 'Survey',
    'description': """
        Add attachment to survey
    """,
    'author': 'cabalcon',
    'website': 'www.cabalcon.com',
    'depends': ['survey'],
    'data': [
        'views/assets.xml',
        'views/survey_question_template.xml',
        'views/survey_user_input_line_view.xml',
    ],
}

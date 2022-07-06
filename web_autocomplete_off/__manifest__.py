# -*- coding: utf-8 -*-
#################################################################################
# Author      : Kanak Infosystems LLP. (<https://www.kanakinfosystems.com/>)
# Copyright(c): 2012-Present Kanak Infosystems LLP.
# All Rights Reserved.
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://www.kanakinfosystems.com/license>
#################################################################################

{
    'name': 'Web Date Field Autocomplete Off',
    'version': '1.0',
    'summary': 'This module is used to Autocomplete off the Date Field across all the models in odoo. | cookie auto complete | history Autocomplete | vallue suggerstion off',
    'description': """
Web Date Field Autocomplete Off
===============================
Web Date Field Autocomplete Off.
    """,
    'category': 'Web',
    'license': 'OPL-1',
    'author': 'Kanak Infosystems LLP.',
    'website': 'https://www.kanakinfosystems.com',
    'images': ['static/description/banner.jpg'],
    'depends': ['web'],
    'data': [
    ],
    'qweb': [
        "static/src/xml/base.xml",
    ],
    'sequence': 1,
    'installable': True,
}

# -*- coding: utf-8 -*-
{
    'name': "Argon Consultora SRL",

    'summary': """
    Modulo que cambia el estilo de la web
    """,

    'description': """
    Modulo que cambia el estilo de la web
    """,

    'author': "HC Sinergia",
    'website': "http://www.hcsinergia.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Theme',
    'version': '1.0',

    # any module necessary for this one to work correctly
    # 'depends': ['base'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/webclient_templates.xml',
        'views/assets.xml',
    ],
    # only loaded in demonstration mode
    # 'demo': [
    #   'demo/demo.xml',
    # ],
}

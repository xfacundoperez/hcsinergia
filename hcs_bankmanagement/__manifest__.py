# -*- coding: utf-8 -*-
{
    'name': "Bank Management",
    'version': '1.0',

    'category': 'Human Resources/Employees',

    'summary': 'Centraliza la información de empleados por compañias',

    'description': """
        Centraliza la información de empleados por compañias
        
        Organizá la plantilla de empleados y salarios por compañía asociada al banco
    """,
    'author': "HC Sinergia",
    'website': "http://www.hcsinergia.com",
    # any module necessary for this one to work correctly
    'depends': ['contacts'],
    # always loaded
    'data': [
        'base/assets.xml',
        'base/webclient_templates.xml',
        #'security/ir.model.access.csv',
        #'views/website_templates.xml',
        #'views/webclient_templates.xml',
        #'views/templates.xml',
        #'views/res_country_views.xml',
        #'views/employee.xml',
        #'views/salary_movement.xml',
        #'views/products.xml',
    ],
    'installable': True,
    'application': True
}

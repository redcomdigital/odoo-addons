{
    'name': 'Campos Personalizados para Contatos - Dados Complementares - Partido Político PT',
    'version': '18.0.1.0.0',
    'category': 'Sales',
    'summary': 'Adiciona campos de filiação, dados eleitorais e setoriais',
    'description': """
        Módulo para gestão de contactos filiados:
        - Dados complementares (CNF, nome social, identidade de género, etc.)
        - Abonador (relacionamento com outro contacto)
        - Dados partidários (filiação/desfiliação, setoriais)
        - Dados eleitorais (título, zona, secção, localização)
    """,
    'author': 'redcom.digital',
    'website': 'https://redcom.digital',
    'license': 'LGPL-3',
    'depends': ['base', 'contacts'],
    'data': [
        'security/ir.model.access.csv',
        'views/res_partner_views.xml',
        'views/sectorial_category_views.xml',
        'data/sectorial_data.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}

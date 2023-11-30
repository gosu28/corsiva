{
    'name': "Lazada Connector",
    'summary': """ Corsiva's ERP system integrates with Lazada """,
    'description': """ Synchronize orders and products between odoo and Lazada """,
    'author': "gosu28",
    'website': "https://gosu28.github.io/sonhh",
    'category': 'Uncategorized',
    'version': '16.0.0.0',
    'depends': [
        'base',
        'corsiva_connector',
        'sale_management',
        'sale_stock',
        'contacts'
    ],
    'data': [
        'data/stock_location.xml',
        'views/lazada_config_settings_views.xml',
        'views/lazada_order_views.xml',
        'views/lazada_partner_views.xml',
        'views/lazada_product_views.xml',
        'views/lazada_attachment_views.xml',
        'views/lazada_product_category_views.xml',
    ],
    'demo': [],
    'assets': {
        'web.assets_backend': [
            'corsiva_lazada/static/src/css/image.css',
        ]
    },
    'post_init_hook': '_stock_post_init',
    'application': True
}

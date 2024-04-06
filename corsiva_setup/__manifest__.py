{
    'name': "Corsiva Setup",
    'summary': """ Corsiva Setup """,
    'description': """ Corsiva Setup """,
    'author': "gosu28",
    'website': "https://gosu28.github.io/sonhh",
    'category': 'Uncategorized',
    'version': '16.0.0.0',
    'depends': [
        'base',
        'stock'
    ],
    'data': [
        'data/stock_location.xml',
        'views/res_config_settings_views.xml',
        'views/product_category_views.xml',
        'views/product_template_views.xml',
        'views/res_partner_views.xml',
        'views/sale_order_views.xml',
    ],
    'post_init_hook': '_stock_post_init',
    'application': False
}

from octb.modules.helpers.base import generate_post
import octb.modules.sql.product as sql

def generate_post_product(product):
    return generate_post(headline=product.name,
                         text=product.description,
                         hashtags=[product.product_type.value,
                                   sql.get_category_by_subcategory_id(product.subcategory_id).name,
                                   sql.get_subcategory_by_id(product.subcategory_id).name
                                   ],
                         args={
                             "цена": product.price,
                         })
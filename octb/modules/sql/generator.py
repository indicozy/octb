from octb.modules.sql.product import add_category, add_subcategory
import yaml

def generate_categories():
    with open("config.yaml", "r") as stream:
        config = yaml.safe_load(stream)
        categories = config['categories']
        for category, subcategories in categories.items():
          category_obj = add_category(category)
          for subcategory in subcategories:
            add_subcategory(subcategory, category_obj.id)
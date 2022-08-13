from octb.modules.sql.product import add_category
import yaml

def generate_categories():
    with open("config.yaml", "r") as stream:
        category_names = yaml.safe_load(stream)
        for category_name in category_names['categories']:
          add_category(category_name)
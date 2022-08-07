from nu_bot.modules.db import add_category, create_tables

import yaml

def run():
    with open("../../../config.yaml", "r") as stream:
        category_names = yaml.safe_load(stream)
        for category_name in category_names['categories']:
          add_category(category_name)

if __name__ == '__main__':
    create_tables()
    run()

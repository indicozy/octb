import threading

from sqlalchemy import Column, Integer, UnicodeText, String, ForeignKey, UniqueConstraint, func, Boolean
from octb.modules.sql import BASE, SESSION

from octb.modules.sql.category import Category
from octb.modules.sql.user import User # needed for Foreignkey, do not delete

# TODO two pooints of truths here in Column() and init
class Product(BASE):
      __tablename__ = "product"

      id = Column(Integer, primary_key=True, autoincrement=True)

      name = Column(String(256), nullable=False)
      has_image = Column(Boolean, default=False)
      description = Column(String(10000), nullable=False)

      is_archived = Column(Boolean, default=False)
      is_selling = Column(Boolean, default=True)
      is_sold = Column(Boolean, default=False)

      message_id = Column(Integer, nullable=False, unique=True)
      seller_id = Column(Integer, ForeignKey("user.user_id"), nullable=False)
      buyer_id = Column(Integer, ForeignKey("user.user_id"), nullable=True)
      category_id = Column(Integer, ForeignKey("category.id"), nullable=False)

      def __init__(self, name, has_image, description, seller_id, category_id, message_id, is_archived=False, is_selling=True, is_sold=False):
        self.name = name 
        self.is_archived = is_archived
        self.has_image = has_image
        self.description = description
        self.seller_id = seller_id
        self.category_id = category_id
        self.message_id = message_id
        self.is_archived = is_archived
        self.is_selling = is_selling
        self.is_sold = is_sold

      def __repr__(self):
          return "<User {} ({})>".format(self.id, self.name)
          o
Product.__table__.create(checkfirst=True)

INSERTION_LOCK = threading.RLock()

def add_product(message_id, is_selling, name, description, seller_id, category_name, has_image):
    category = SESSION.query(Category).where(Category.name == category_name).first() # TODO try except
    with INSERTION_LOCK:
        product = Product(name, has_image, description, seller_id, category.id, message_id, is_selling=is_selling)
        SESSION.add(product)
        SESSION.flush()
        SESSION.commit()

def get_products_from_tg_user(tg_id):
    try:
        return SESSION.query(Product)\
          .where(Product.seller_id == tg_id)\
          .all()
    finally:
        SESSION.close()

def get_product_by_id(product_id, tg_id, seller=True):
    query = SESSION.query(Product)\
            .where(Product.id == product_id)
    if seller==True:
      query = query.where(Product.seller_id == tg_id)
    else:
      query = query.where(Product.buyer == tg_id)
    try:
        return query.first()
    finally:
      SESSION.close()
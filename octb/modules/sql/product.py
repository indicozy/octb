import threading

from sqlalchemy import Column, Integer, UnicodeText, String, ForeignKey, UniqueConstraint, func, Boolean, Enum
from octb.modules.sql import BASE, SESSION

from octb.modules.sql.user import User # needed for Foreignkey, do not delete
import enum

INSERTION_LOCK = threading.RLock()

class Category(BASE):
      __tablename__ = "category"

      id = Column(Integer, primary_key=True, autoincrement=True)
      name = Column(String(64), unique=True)

      def __init__(self, name):
          self.name = name 

      def __repr__(self):
          return "<User {} ({})>".format(self.id, self.name)
Category.__table__.create(checkfirst=True)

class Subcategory(BASE):
      __tablename__ = "subcategory"

      id = Column(Integer, primary_key=True, autoincrement=True)
      category_id = Column(Integer, ForeignKey("category.id"), nullable=False)

      name = Column(String(256), nullable=False)

      def __init__(self, category_id, name):
        self.name = name
        self.category_id = category_id

      def __repr__(self):
          return "<Subcategory {} ({})>".format(self.id, self.name)
Market_subcategory.__table__.create(checkfirst=True)

def get_all_categories():
    try:
        return SESSION.query(Category).all()
    finally:
        SESSION.close()

def get_category_by_name(name):
    try:
        return SESSION.query(Category).where(Category.name == name).first()
    finally:
        SESSION.close()

def get_category_by_id(category_id):
    try:
        return SESSION.query(Category).where(Category.id == category_id).first()
    finally:
        SESSION.close()

def add_category(category_name):
    with INSERTION_LOCK:
        category = SESSION.query(Category).where(Category.name==category_name).all()
        if len(category) == 0:
            category = Category(category_name)
            SESSION.add(category)
            SESSION.flush()
        SESSION.commit()
        
class ProductTypeEnum(enum.Enum):
    sell = 'продаю'
    buy = 'куплю'
    lend = 'сдаю'
    borrow = 'одолжу'
    give = 'отдам'

# TODO two pooints of truths here in Column() and init
class Product(BASE):
      __tablename__ = "product"

      id = Column(Integer, primary_key=True, autoincrement=True)
      seller_id = Column(Integer, nullable=False)
      category_id = Column(Integer, ForeignKey("category.id"), nullable=False)
      message_id = Column(Integer, nullable=False, unique=True)

      name = Column(String(256), nullable=False)
      has_image = Column(Boolean, default=False)
      description = Column(String(10000), nullable=False)
      product_type = Column(Enum(ProductTypeEnum))

      is_archived = Column(Boolean, default=False)
      is_sold = Column(Boolean, default=False)

      def __init__(self, name, has_image, description, product_type, seller_id, category_id, message_id, is_archived=False, is_sold=False):
        self.name = name 
        self.is_archived = is_archived
        self.has_image = has_image
        self.description = description
        self.seller_id = seller_id
        self.category_id = category_id
        self.message_id = message_id
        self.is_archived = is_archived
        self.product_type = product_type
        self.is_sold = is_sold

      def __repr__(self):
          return "<Product {} ({})>".format(self.id, self.name)
Product.__table__.create(checkfirst=True)

class Product_buyer(BASE):
      __tablename__ = "product_buyer"

      id = Column(Integer, primary_key=True, autoincrement=True)

      product_id = Column(Integer, ForeignKey("product.id"), nullable=False)
      buyer_id = Column(Integer, nullable=False) # user.id

      def __init__(self, product_id, buyer_id):
        self.product_id = product_id 
        self.buyer_id = buyer_id 

      def __repr__(self):
          return "<Product Buyer {} ({})>".format(self.id, self.buyer_id)

Product_buyer.__table__.create(checkfirst=True)

def add_buyer(product_id, buyer_id):
    with INSERTION_LOCK:
        product_buyer = SESSION.query(Product_buyer)\
          .where(Product_buyer.buyer_id==buyer_id)\
          .where(Product_buyer.product_id==product_id).all() # TODO change to new one https://stackoverflow.com/questions/41636169/how-to-use-postgresqls-insert-on-conflict-upsert-feature-with-flask-sqlal
        if len(product_buyer) == 0:
            product_buyer = Product_buyer(product_id, buyer_id)
            SESSION.add(product_buyer)
            SESSION.flush()
        SESSION.commit()

def add_product(message_id, product_type, name, description, seller_id, category_name, has_image):
    category = SESSION.query(Category).where(Category.name == category_name).first() # TODO try except
    with INSERTION_LOCK:
        product = Product(name, has_image, description, product_type, seller_id, category.id, message_id)
        SESSION.add(product)
        SESSION.flush()
        SESSION.commit()
    return product

def archive_product(product_id, user_id):
    with INSERTION_LOCK:
        product = SESSION.query(Product)\
          .where(Product.id == product_id)\
          .where(Product.seller_id == user_id)\
          .first() # TODO try except
        product.is_archived = True
        SESSION.add(product)
        SESSION.commit()
        return product

def product_sold(product_id, user_id):
    with INSERTION_LOCK:
        product = SESSION.query(Product)\
          .where(Product.id == product_id)\
          .where(Product.seller_id == user_id)\
          .first() # TODO try except
        product.is_sold = True
        SESSION.add(product)
        SESSION.commit()
        return product

def product_restore(product_id, user_id):
    with INSERTION_LOCK:
        product = SESSION.query(Product)\
          .where(Product.id == product_id)\
          .where(Product.seller_id == user_id)\
          .first() # TODO try except
        product.is_sold = False
        SESSION.add(product)
        SESSION.commit()
        return product

def get_products_from_tg_user(tg_id):
    try:
        return SESSION.query(Product)\
          .where(Product.seller_id == tg_id)\
          .all()
    finally:
        SESSION.close()

def get_active_products_from_tg_user(tg_id):
    try:
        return SESSION.query(Product)\
          .where(Product.seller_id == tg_id)\
          .where(Product.is_archived == False)\
          .all()
    finally:
        SESSION.close()

def get_product_by_id(product_id, tg_id):
    query = SESSION.query(Product)\
            .where(Product.id == product_id)
    query = query.where(Product.seller_id == tg_id)
    try:
        return query.first()
    finally:
      SESSION.close()

def get_product_by_id_no_verify(product_id):
    query = SESSION.query(Product)\
            .where(Product.id == product_id)
    try:
        return query.first()
    finally:
      SESSION.close()

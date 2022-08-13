import threading

from sqlalchemy import Column, Integer, UnicodeText, String, ForeignKey, UniqueConstraint, func, Boolean, DateTime
from sqlalchemy.sql import func

from octb.modules.sql import BASE, SESSION

from octb.modules.sql.product import Category
from octb.modules.sql.user import User # needed for Foreignkey, do not delete

# TODO two pooints of truths here in Column() and init
class Market_product(BASE):
      __tablename__ = "market_product"

      id = Column(Integer, primary_key=True, autoincrement=True)
      seller_id = Column(Integer, ForeignKey("user.user_id"), nullable=False)
      subcategory_id = Column(Integer, ForeignKey("market_subcategory.id"), nullable=False)

      name = Column(String(256), nullable=False)
      has_image = Column(Boolean, default=False)

      is_archived = Column(Boolean, default=False)
      is_sold = Column(Boolean, default=False)


      def __init__(self, seller_id, subcategory_id, name, has_image=False, is_archived=False, is_sold = False):
        self.name = name
        self.seller_id = seller_id
        self.subcategory_id = subcategory_id
        self.has_image = has_image
        self.is_archived = is_archived
        self.is_sold = is_sold

      def __repr__(self):
          return "<Market Item {} ({})>".format(self.id, self.name)
Market_item.__table__.create(checkfirst=True)

class Market_buyer(BASE):
      __tablename__ = "market_buyer"

      id = Column(Integer, primary_key=True, autoincrement=True)

      product_id = Column(Integer, ForeignKey("market_product.id"), nullable=False)
      buyer_id = Column(Integer, nullable=False) # user.id

      def __init__(self, product_id, buyer_id):
        self.product_id = product_id 
        self.buyer_id = buyer_id 

      def __repr__(self):
          return "<Market Buyer {} ({})>".format(self.id, self.buyer_id)

Market_buyer.__table__.create(checkfirst=True)

class Market_seller(BASE):
      __tablename__ = "market_seller"

      user_id = Column(Integer, primary_key=True)
      name = Column(String(256), nullable=False)

      created_at = Column(DateTime(timezone=True), server_default=func.now())
      updated_at = Column(DateTime(timezone=True), onupdate=func.now())

      def __init__(self, user_id, name):
        self.user_id = user_id
        self.name = name

      def __repr__(self):
          return "<Market Seller {} ({})>".format(self.id, self.name)
Market_seller.__table__.create(checkfirst=True)

class Market_rating(BASE):
      __tablename__ = "market_rating"

      user_id = Column(Integer, primary_key=True)
      product_id = Column(Integer, ForeignKey("market_product.user_id"), nullable=False)

      rating = Column(Integer, nullable=False)
      body = Column(String(2048), nullable=False)

      created_at = Column(DateTime(timezone=True), server_default=func.now())

      def __init__(self, user_id, product_id, rating, body):
        self.user_id = user_id
        self.product_id = product_id
        self.rating = rating
        self.body = body

      def __repr__(self):
          return "<Market Rating {} ({})>".format(self.id, self.name)
Market_rating.__table__.create(checkfirst=True)

class Market_subcategory(BASE):
      __tablename__ = "market_subcategory"

      id = Column(Integer, primary_key=True, autoincrement=True)
      category_name = Column(String(256), nullable=False)

      name = Column(String(256), nullable=False)

      def __init__(self, category_name, name):
        self.name = name
        self.category_name = category_name

      def __repr__(self):
          return "<Market Subcategory {} ({})>".format(self.id, self.name)
Market_subcategory.__table__.create(checkfirst=True)

INSERTION_LOCK = threading.RLock()
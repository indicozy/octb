import threading

from sqlalchemy import Column, Integer, UnicodeText, String, ForeignKey, UniqueConstraint, func, Boolean
from octb.modules.sql import BASE, SESSION

from octb.modules.sql.product import Category
from octb.modules.sql.user import User # needed for Foreignkey, do not delete

# TODO two pooints of truths here in Column() and init
class Market_item(BASE):
      __tablename__ = "Market_product"

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
      subcategory_id = Column(Integer, ForeignKey("subcategory_id.id"), nullable=False)

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
          return "<Market Item {} ({})>".format(self.id, self.name)
Market_item.__table__.create(checkfirst=True)

INSERTION_LOCK = threading.RLock()
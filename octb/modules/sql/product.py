import threading

from sqlalchemy import Column, Integer, UnicodeText, String, ForeignKey, UniqueConstraint, func
from octb.modules.sql import BASE, SESSION

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
      seller_id = Column(Integer, ForeignKey("user.id"), nullable=False)
      buyer_id = Column(Integer, ForeignKey("user.id"), nullable=True)
      category_id = Column(Integer, ForeignKey("category.id"), nullable=False)

      def __init__(self, name, has_image, description, seller_id, category_id, is_archived=False, is_selling=True, is_sold=False):
        self.name = name 
        self.is_archived = is_archived
        self.has_image = has_image
        self.description = description
        self.seller_id = seller_id
        self.category_id = category_id
        self.is_archived = is_archived
        self.is_selling = is_selling
        self.is_sold = is_sold

      def __repr__(self):
          return "<User {} ({})>".format(self.id, self.name)
          o
Product.__table__.create(checkfirst=True)

INSERTION_LOCK = threading.RLock()

def add_product(message_id, is_selling, name, description, seller_tg_id, category_name, has_image):
    category = None
    seller = None

    results = None

    with Session() as session:
      category = Category(name=category_name)
      category_stmt = select(Category).where(Category.name == category_name)
      category = session.scalars(category_stmt).one()

      seller = User(tg_id=seller_tg_id)
      seller_stmt = select(User).where(User.tg_id == seller_tg_id)
      seller = session.scalars(seller_stmt).one()

    with engine.connect() as conn:
        product_new = insert(Product).values(message_id=message_id, is_selling=is_selling, name=name, description=description, seller_id=seller.id, category_id=category.id, has_image=has_image)\
          .returning(Product.id)
        results = conn.execute(product_new)
        conn.commit()
    return results.first()[0]# TODO refactor it's id of product

def get_products_from_tg_user(tg_id):
    with Session() as session:
        stmt = select(Product)\
          .join(Product.seller)\
          .where(User.tg_id == tg_id)
        results = session.scalars(stmt).all()
    return results

def get_product_by_id(product_id, tg_id, seller=True):
    results = None
    with Session().begin() as session:
      if seller==True:
        stmt = select(Product)\
          .join(Product.seller)\
          .where(User.tg_id == tg_id)
      else:
        stmt = select(Product)\
          .join(Product.buyer)\
          .where(User.tg_id == tg_id)\
          .where(Product.id == product_id)
      results = session.scalars(stmt).first()
      print(results)
    return results
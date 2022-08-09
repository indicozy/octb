import threading

from sqlalchemy import Column, Integer, UnicodeText, String, ForeignKey, UniqueConstraint, func
from octb.modules.sql import BASE, SESSION

class Category(BASE):
      __tablename__ = "category"

      id = Column(Integer, primary_key=True, autoincrement=True)
      name = Column(String(64), unique=True)

      def __init__(self, name):
          self.name = name 

      def __repr__(self):
          return "<User {} ({})>".format(self.id, self.name)

Category.__table__.create(checkfirst=True)

INSERTION_LOCK = threading.RLock()

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
        category = SESSION.query(Category).where(Category.name==category_name)
        if not category:
            category = Category(category_name)
            SESSION.add(category)
            SESSION.flush()
        SESSION.commit()
import threading

from sqlalchemy import Column, Integer, UnicodeText, String, ForeignKey, UniqueConstraint, func, DateTime, BigInteger
from octb.modules.sql import BASE, SESSION

class User(BASE):
      __tablename__ = "user"

      user_id = Column(BigInteger, primary_key=True)
      username = Column(UnicodeText)

      created_at = Column(DateTime(timezone=True), server_default=func.now())
      updated_at = Column(DateTime(timezone=True), onupdate=func.now())

      def __init__(self, user_id, username=None):
          self.user_id = user_id
          self.username = username

      def __repr__(self):
          return "<User {} ({})>".format(self.username, self.user_id)

User.__table__.create(checkfirst=True)

INSERTION_LOCK = threading.RLock()

def get_users_all():
  try:
    return SESSION.query(User)\
      .all()
  finally:
      SESSION.close()

def update_user(user_id, username):
  with INSERTION_LOCK:
    user = SESSION.query(User).get(user_id)
    if not user:
      user = User(user_id, username=username)
      SESSION.add(user)
    else:
      user.username = username
    SESSION.commit()
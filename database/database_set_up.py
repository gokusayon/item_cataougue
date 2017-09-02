#!/usr/bin/python
# -*- coding: utf-8 -*-

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy import create_engine


Base = declarative_base()


class User(Base):

    """This class is used as user table modal"""

    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String(16), nullable=False)
    email = Column(String(30), nullable=False)
    picture = Column(String(100), nullable=False)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            # 'picture': self.picture
        }


class Catagory(Base):

    """This class is used as catagory table modal"""

    __tablename__ = 'catagory'
    id = Column(Integer, primary_key=True)
    name = Column(String(16), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User, backref="catagory")
    items = relationship("Item", cascade="all")

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'id': self.id,
            'user': self.user.serialize
        }


class Item(Base):

    """This class is used as item table modal"""

    __tablename__ = 'item'
    id = Column(Integer, primary_key=True)
    name = Column(String(16), nullable=False)
    description = Column(String(100), nullable=False)
    image_url = Column(String(100), nullable=False)
    catagory_id = Column(Integer, ForeignKey('catagory.id'))
    user_id = Column(Integer, ForeignKey('user.id'))
    created_by = relationship(User)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'image_url': self.image_url,
            'description': self.description,
            'catagory_id': self.catagory_id,
            'created_by': self.created_by.serialize
        }


engine = create_engine('mysql+pymysql://root:root@localhost/item_catalog')

Base.metadata.create_all(engine)

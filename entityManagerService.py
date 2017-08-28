#!/usr/bin/python
# -*- coding: utf-8 -*-
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from database_set_up import Base, Catagory, Item, User

import logging

logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

engine = \
    create_engine('mysql+pymysql://root:root@localhost/item_catalog')
Base.metadata.bind = engine
database_session = sessionmaker(bind=engine)
session = database_session()


class UserService:

    """docstring for UserService"""

    def getAllUsers(self):
        userList = session.query(User).all()
        serializedUserList = [user.serialize for user in userList]
        return serializedUserList

    def getUserByNameAndId(self, user_name, email_id):
        return session.query(User).filter_by(name=user_name,
                                             email=email_id).one()

    def save(self, auth_session):
        session.add(user)
        session.commit()


class CatagoryService:

    """docstring for UserService"""

    def getAllCatagories(self):
        catagoryList = session.query(Catagory).all()
        serializedCatagoryList = [catagory.serialize for catagory in
                                  catagoryList]
        return serializedCatagoryList

    def getCatagoryById(self, catagory_id):
        return session.query(Catagory).filter_by(id=catagory_id).one()

    def getCatagoryByName(self, catagory_name):
        return session.query(Catagory).filter_by(name=catagory_name).one()

    def getCatagoriesList(self):
        return session.query(Catagory).order_by(Catagory.name)


class ItemService:

    """docstring for UserService"""

    def getAllItems(self):
        itemList = session.query(Item).all()
        serializedItemList = [item.serialize for item in itemList]
        return serializedItemList

    def getJson(self, item_id):
        item = session.query(Item).filter_by(id=item_id).one()
        serializedItem = item.serialize
        return serializedItem

    def getItemById(self, item_id):
        return session.query(Item).filter_by(id=item_id).one()

    def getItemByName(self, item_name):
        return session.query(Item).filter_by(name=item_name).one()

    def getItemByNameAndCatagory(self, catagory_id, item_name):
        return session.query(Item).filter_by(catagory_id=catagory_id,
                                             name=item_name).one()

    def getItemsForCatagory(self, catagory_id):
        return session.query(Item).filter_by(catagory_id=catagory_id).all()

    def getItemList(self):
        return session.query(Item).limit(10)

    def deleteItemById(self, item_id):
        session.query(Item).filter_by(id=item_id).delete()
        session.commit()


class EntityManagerService:

    def getUserBy(self, userName):
        return session.query(User).filter_by(name=userName).all()

    def getUserById(self, user_id):
        return session.query(User).filter_by(id=user_id).one()

    def save(self, new_or_updated_object):
        session.add(new_or_updated_object)
        session.commit()
        return

    def delete(self, item):
        session.delete(item)
        session.commit()
        return

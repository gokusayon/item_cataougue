#!/usr/bin/python
# -*- coding: utf-8 -*-

from entityManagerService import EntityManagerService
from database_set_up import Base, Catagory, Item, User

eMS = EntityManagerService()

user = User(name='Vasu Sheoran', email='vasumcs@live.com',
            picture='http://some-dummy-image.jpeg')

eMS.save(user)

Catagory1 = Catagory(name='Football', user_id=1)
eMS.save(Catagory1)

Catagory2 = Catagory(name='Cars', user_id=1)
eMS.save(Catagory2)

Catagory3 = Catagory(name='Snacks', user_id=1)
eMS.save(Catagory3)

Catagory4 = Catagory(name='Gadgets', user_id=1)
eMS.save(Catagory4)

Catagory5 = Catagory(name='Food', user_id=1)
eMS.save(Catagory5)

# Populate a Catagory with Item for testing

Item1 = Item(name='Football Boots',
             description='Shoes to play football in.',
             image_url='https://www.intersport.co.uk/images\
             /mens-nike-mercurial-victory-vi-cr7-dynamic-fit-fg-firm-\
             ground-grey-football-boot-p4458-11917_image.jpg', catagory_id=1,
             user_id=1)
eMS.save(Item1)

print 'Your dabase has been set up'
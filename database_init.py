#!/usr/bin/python
# -*- coding: utf-8 -*-

from entityManagerService import EntityManagerService
from database_set_up import Base, Catagory, Item, User

eMS = EntityManagerService()

user = User(name='Vasu Sheoran', email='vasumcs@live.com',
            picture='http://dummyimage.com/200x200.png/ff4444/ffffff')

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
# Using different users for Item also

Item1 = Item(name='Football Boots',
             description='Shoes to play football in.',
             image_url='http://bit.ly/2qHbHxd', catagory_id=1,
             user_id=1)
eMS.save(Item1)

Item1 = Item(name='Football Boots',
             description='Shoes to play football in.',
             image_url='http://bit.ly/2qHbHxd', catagory_id=1,
             user_id=1)

i = Item(name='Football Boots', description='Shoes to play football in.',
         image_url='http://bit.ly/2qHbHxd', catagory_id=3, user_id=1)
eMS.save(i)
r = Item(name='Football Boots', description='Shoes to play football in.',
         image_url='http://bit.ly/2qHbHxd', catagory_id=4, user_id=1)
eMS.save(r)
t = Item(name='Football Boots', description='Shoes to play football in.',
         image_url='http://bit.ly/2qHbHxd', catagory_id=2, user_id=1)
eMS.save(t)

Item2 = Item(name='Football Shirt',
             description='Shirt to play football in.',
             image_url='http://bit.ly/2pb59qn', catagory_id=1,
             user_id=1)
eMS.save(Item2)

Item3 = Item(name='Football', description='A Football.',
             image_url='http://bit.ly/2pJSPR1', catagory_id=1,
             user_id=1)
eMS.save(Item3)

print 'Your dabase has been set up'
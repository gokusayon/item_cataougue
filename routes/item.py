from flask import Blueprint, render_template, abort,request,flash,redirect,jsonify,url_for
from jinja2 import TemplateNotFound
from flask import session as login_session


from database.entityManagerService import EntityManagerService, CatagoryService, ItemService, UserService
from database.database_set_up import User,Item,Catagory

import requests

item_routes = Blueprint('item', __name__,
                        template_folder='templates')


# Services for CRUD operations
eMS = EntityManagerService()
userService = UserService()
catagoryService = CatagoryService()
itemService = ItemService()

def isLoggedIn():
    access_token = login_session.get('access_token')
    if access_token is None:
        return False
    else:
        return True

# Add an item
@item_routes.route('/catalog/<path:catagory_name>/add', methods=['GET','POST'])
def addItem(catagory_name):
	try:
		# Validate if current user is logged in
	    if isLoggedIn():
	        catagory = catagoryService.getCatagoryByName(catagory_name)
	        user = userService.getUserByNameAndId(login_session['username'],login_session['email'])

            # Anyone can add item to acatagory but not edit and delete
            if request.method == 'POST':
                exists = itemService.isPresent(request.form['name'],catagory.id)

                if exists:
                    flash('This item already exists. Duplicate entries are are not allowed!')
                    return redirect(url_for('catagory.showCatalog'))

                else:
                    newItem = Item(name= request.form['name'],
    	               description= request.form['description'],
    	               image_url= request.form['image_url'],
    	               catagory_id=catagory.id,
    	               user_id=user.id)
    	            eMS.save(newItem)
    	            flash('Category Item Successfully Created!')
    	            return redirect(url_for('catagory.showCatalog'))

	    return render_template("addItem.html",catagory_name=catagory_name, isLoggedIn=isLoggedIn())

	except TemplateNotFound:
		abort(404)

# Display a Specific Item
@item_routes.route('/catalog/<path:catagory_name>/<path:item_id>/')
def showItem(catagory_name, item_id):
    item = itemService.getItemById(item_id)
    return render_template('item.html', catagory_name=catagory_name, item=item, show_welcome="false", isLoggedIn=isLoggedIn())


# Edit an item
@item_routes.route('/catalog/<path:catagory_name>/<path:item_name>/edit', methods=['GET', 'POST'])
def editItem(catagory_name, item_name):
    
    # Validate if current user is logged in
    if isLoggedIn():
        catagory = catagoryService.getCatagoryByName(catagory_name)
        item = itemService.getItemByNameAndCatagory(catagory.id, item_name)
        user = userService.getUserByNameAndId(login_session['username'],login_session['email'])
        
        # If catagory is not created by current user then do nothing else proceed
        if item.user_id == user.id and request.method == 'POST':
            item.name = request.form['name']
            item.description = request.form['description']
            item.image_url = request.form['image_url']
            eMS.save(item)
            flash('Category Item Successfully Edited!')
            return redirect(url_for('catagory.showCategory', catagory_name=catagory_name,item_id = item.id))


        elif item.user_id != user.id :
            flash('You do not have access to edit this item! ')
            return redirect(url_for('catagory.showCategory', catagory_name=catagory_name,item_id = item.id))

    return render_template('edititem.html',
                           catagory_name=catagory_name,item=item, isLoggedIn=isLoggedIn())

# Remove Item
@item_routes.route('/catalog/<path:catagory_name>/<path:item_name>/delete', methods=['GET', 'POST'])
def removeItem(catagory_name,item_name):
    
    # Validate if current user is logged in
    if isLoggedIn():
        catagory = catagoryService.getCatagoryByName(catagory_name)
        item = itemService.getItemByNameAndCatagory(catagory.id, item_name)
        user = userService.getUserByNameAndId(login_session['username'],login_session['email'])
        if item.user_id == user.id:
            eMS.delete(item)
            flash('Category Item Successfully Deleted!')
        else:
            flash('You do not have access to delete this item! ')

    return redirect(url_for('catagory.showCategory', catagory_name=catagory_name))
        


# to get items
@item_routes.route('/items.json')
def getAllItems():
    items = itemService.getAllItems()
    return jsonify(items)

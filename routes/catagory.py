from flask import Blueprint, render_template, abort,request,flash,redirect,jsonify,url_for
from jinja2 import TemplateNotFound
from flask import session as login_session
import json


from database.entityManagerService import EntityManagerService, CatagoryService, ItemService, UserService
from database.database_set_up import User,Item,Catagory

import requests

catagory_routes = Blueprint('catagory', __name__,
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


# Default Mapping
@catagory_routes.route('/')
@catagory_routes.route('/catalog/')
def showCatalog():
    categories = catagoryService.getCatagoriesList()
    items = itemService.getItemList()
    isUserLoggedIn = isLoggedIn()
    if isUserLoggedIn == True:
        userName = login_session['username']
        userImage = login_session['picture']
    else:
        userName = ""
        userImage = ""

    return render_template('catagories.html', categories=categories,show_welcome='true', items=items, isLoggedIn=isUserLoggedIn, user_name=userName, user_image=userImage)



# Add a category
@catagory_routes.route('/catalog/addcategory', methods=['GET', 'POST'])
def addCatagory():    

    # Validate if current user is logged in
    if isLoggedIn():
        if request.method == 'POST':
            user = userService.getUserByNameAndId(login_session['username'],login_session['email'])
            exists = catagoryService.isPresent(request.form['name'])

            if exists:
                flash('This Catagory already exists. Duplicate entries are are not allowed!')
                return redirect(url_for('catagory.showCatalog'))

            else:

                catagory = Catagory(name=request.form['name'],
                          user_id=user.id)
                eMS.save(catagory)
                flash('Category Successfully Created!')
                return redirect(url_for('catagory.showCatalog'))

        else:
            return render_template('addCatagory.html',show_welcome="false", isLoggedIn=isLoggedIn())

    else:
        return render_template('addCatagory.html',show_welcome="false", isLoggedIn=isLoggedIn())

# Edit a category 
@catagory_routes.route('/catalog/<path:catagory_name>/edit', methods=['GET', 'POST'])
def editCategory(catagory_name):
    
    catagory = catagoryService.getCatagoryByName(catagory_name)
    # Validate if current user is logged in
    if isLoggedIn():

        user = userService.getUserByNameAndId(login_session['username'],login_session['email'])

        # If user exists and is logged in
        if bool(user) == True:

            # If catagory is not created by current user then do nothing else proceed to `elif`
            if catagory.user_id != user.id :
                flash('You do not have access to edit this item!')
                return redirect(url_for('catagory.showCatalog'))

            elif request.method == 'POST' and bool(request.form['name']):
    	    	catagory.name = request.form['name']
    	    	eMS.save(catagory)
    	    	flash('Category Item Successfully Edited!')
    	    	return redirect(url_for('catagory.showCatalog'))

    # If user not logged in or does not have access to modify template then return editcatagory.html
    return render_template('editcategory.html',
                           catagory_name=catagory_name,show_welcome="false", isLoggedIn=isLoggedIn())

# Delete a category
@catagory_routes.route('/catalog/<path:catagory_name>/delete', methods=['GET', 'POST'])
def removeCategory(catagory_name):
    try:
        # Validate if current user is logged in
        isUserLoggedIn = isLoggedIn()

        # Validate if current user is logged in
        if isUserLoggedIn:
            catagory = catagoryService.getCatagoryByName(catagory_name)
            user = userService.getUserByNameAndId(login_session['username'],login_session['email'])
            # If catagory is not created by current user then do nothing else proceed to `elif`
            if catagory.user_id == user.id:
                eMS.delete(catagory)
                flash('Item Deleted Successfully')
                return redirect(url_for('catagory.showCatalog'))

            else:
                flash('You do not have access to delete this item!' )

        # If user not logged in or does not have access to modify template then render showCatalog
        return redirect(url_for('catagory.showCatalog'))
    except TemplateNotFound:
        abort(404)

# Show Category Items
@catagory_routes.route('/catalog/<path:catagory_name>/items/')
def showCategory(catagory_name):
    catagory = catagoryService.getCatagoryByName(catagory_name)
    catagory_id = catagory.id
    categories = catagoryService.getCatagoriesList()
    items = itemService.getItemsForCatagory(catagory.id)
    count = items.__len__()
    isUserLoggedIn = isLoggedIn()
    if isUserLoggedIn == True:
        userName = login_session['username']
        userImage = login_session['picture']
        show_welcome = 'true'
    else:
        userName = ""
        userImage = ""
        show_welcome='false'

    return render_template('items.html', categories=categories, show_welcome=show_welcome, catagory_name=catagory_name, catagory_id=catagory_id, items=items, count=count, isLoggedIn=isUserLoggedIn, user_name=userName, user_image=userImage)


# to get catagories
@catagory_routes.route('/catagories.json')
def getAllCatagories():
    catagories = catagoryService.getAllCatagories()
    return jsonify(catagories)
#!/usr/bin/env python

from flask import Flask, render_template, jsonify, request, flash, redirect, url_for, make_response
from database.entityManagerService import EntityManagerService, CatagoryService, ItemService, UserService
from database.database_set_up import User,Item,Catagory

from flask import session as login_session
import random
import string


# IMPORTS FOR Googel Authentication
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
import requests

app = Flask(__name__)

# Load secret key from file
CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Item Cataloge"

app = Flask(__name__)

# Services for CRUD operations
eMS = EntityManagerService()
userService = UserService()
catagoryService = CatagoryService()
itemService = ItemService()


@app.route('/login')
def showLogin():

    """ Creates a session state and renders login.html. """
    
    state = ''.join(
        random.choice(string.ascii_uppercase + string.digits) for x in range(32))
    login_session['state'] = state
    return render_template('login.html',show_welcome="false", STATE=state, isLoggedIn=isLoggedIn())

@app.route('/gconnect', methods=['POST'])
def gconnect():

    """ Gathers data from Google Sign In API and places it inside a session variable. """

    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps(
            'Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets(
            'client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    try:
    	user = userService.getUserByNameAndId(login_session['username'],login_session['email'] )
    except:
    	user = User(name = data["name"],email = data["email"],picture =data["picture"])
    	eMS.save(user)

    flash("you are now logged in as %s" % login_session['username'])
    return "True"

    # DISCONNECT - Revoke a current user's token and reset their
    # login_session

# Removes the session from cacche
@app.route('/remove/session')
def removeLoginSession():
	del login_session['access_token']
	del login_session['gplus_id']
	del login_session['username']
	del login_session['email']
	del login_session['picture']
	return "Done"

# Logout from google server
@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(json.dumps(
            'Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session[
        'access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps(
            'Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return redirect(url_for('showCatalog'))
    else:
        response = make_response(json.dumps(
            'Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


def isLoggedIn():
    access_token = login_session.get('access_token')
    if access_token is None:
        return False
    else:
        return True


# Show Category Items
@app.route('/catalog/<path:catagory_name>/items/')
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

# Display a Specific Item
@app.route('/catalog/<path:catagory_name>/<path:item_id>/')
def showItem(catagory_name, item_id):
    item = itemService.getItemById(item_id)
    return render_template('item.html', catagory_name=catagory_name, item=item, show_welcome="false", isLoggedIn=isLoggedIn())

# Add a category
@app.route('/catalog/addcategory', methods=['GET', 'POST'])
def addCatagory():    

    # Validate if current user is logged in
    if isLoggedIn():
        if request.method == 'POST':
            user = userService.getUserByNameAndId(login_session['username'],login_session['email'])
            catagory = Catagory(name=request.form['name'],
                          user_id=user.id)
            eMS.save(catagory)
            flash('Category Successfully Created!')
            return redirect(url_for('showCatalog'))

        else:
            return render_template('addCatagory.html',show_welcome="false", isLoggedIn=isLoggedIn())

    else:
        return render_template('addCatagory.html',show_welcome="false", isLoggedIn=isLoggedIn())

# Edit a category 
@app.route('/catalog/<path:catagory_name>/edit', methods=['GET', 'POST'])
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
                return redirect(url_for('showCatalog'))

            elif request.method == 'POST' and bool(request.form['name']):
    	    	catagory.name = request.form['name']
    	    	eMS.save(catagory)
    	    	flash('Category Item Successfully Edited!')
    	    	return redirect(url_for('showCatalog'))

    # If user not logged in or does not have access to modify template then return editcatagory.html
    return render_template('editcategory.html',
                           catagory_name=catagory_name,show_welcome="false", isLoggedIn=isLoggedIn())

# Delete a category
@app.route('/catalog/<path:catagory_name>/delete', methods=['GET', 'POST'])
def removeCategory(catagory_name):
    # Validate if current user is logged in
    isUserLoggedIn = isLoggedIn()

    # Validate if current user is logged in
    if isUserLoggedIn:
        catagory = catagoryService.getCatagoryByName(catagory_name)
        user = userService.getUserByNameAndId(login_session['username'],login_session['email'])

        # If catagory is not created by current user then do nothing else proceed to `elif`
        if catagory.user_id == user.id:
            catagory = catagoryService.getCatagoryByName(catagory_name)
            eMS.delete(catagory)
            flash('Item Deleted Successfully')
            return redirect(url_for('showCatalog'))

        else:
            flash('You do not have access to delete this item!' )

    # If user not logged in or does not have access to modify template then render showCatalog
    return redirect(url_for('showCatalog'))


# Add an item
@app.route('/catalog/<path:catagory_name>/add', methods=['GET','POST'])
def addItem(catagory_name):
    # Validate if current user is logged in
    if isLoggedIn():
        catagory = catagoryService.getCatagoryByName(catagory_name)
        user = userService.getUserByNameAndId(login_session['username'],login_session['email'])

        # Anyone can add item to acatagory but not edit and delete
        if request.method == 'POST':
            item = Item(name= request.form['name'],
               description= request.form['description'],
               image_url= request.form['image_url'],
               catagory_id=catagory.id,
               user_id=user.id)
            eMS.save(item)
            flash('Category Item Successfully Created!')
            return redirect(url_for('showCatalog'))

    return render_template("addItem.html",catagory_name=catagory_name, isLoggedIn=isLoggedIn())

# Edit an item
@app.route('/catalog/<path:catagory_name>/<path:item_name>/edit', methods=['GET', 'POST'])
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
            return redirect(url_for('showCategory', catagory_name=catagory_name,item_id = item.id))


        elif item.user_id != user.id :
            flash('You do not have access to edit this item! ')
            return redirect(url_for('showCategory', catagory_name=catagory_name,item_id = item.id))

    return render_template('edititem.html',
                           catagory_name=catagory_name,item=item, isLoggedIn=isLoggedIn())

# Remove Item
@app.route('/catalog/<path:catagory_name>/<path:item_name>/delete', methods=['GET', 'POST'])
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

    return redirect(url_for('showCategory', catagory_name=catagory_name))
        


# Default Mapping
@app.route('/')
@app.route('/catalog/')
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

# JSON endpoints 

# to get all users
@app.route('/json/user')
def getAllUsers():
    users = userService.getAllUsers()
    return jsonify(users)

# to get catagories
@app.route('/json/catagories')
def getAllCatagories():
    catagories = catagoryService.getAllCatagories()
    return jsonify(catagories)

# to get items
@app.route('/json/items')
def getAllItems():
    items = itemService.getAllItems()
    return jsonify(items)

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.run(host='localhost', port=8080, debug=True)

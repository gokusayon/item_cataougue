from flask import Flask, render_template, jsonify, request, flash, redirect, url_for, make_response
from database.entityManagerService import EntityManagerService, CatagoryService, ItemService, UserService
from database.database_set_up import User,Item,Catagory

from flask import session as login_session
import random
import string


# IMPORTS FOR THIS STEP
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
import requests

app = Flask(__name__)


CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Item Cataloge"

app = Flask(__name__)

eMS = EntityManagerService()
userService = UserService()
catagoryService = CatagoryService()
itemService = ItemService()


@app.route('/login')
def showLogin():
    state = ''.join(
        random.choice(string.ascii_uppercase + string.digits) for x in range(32))
    login_session['state'] = state
    # return "The current session state is %s" %
    # login_session['state']
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
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
        print("Token's client ID does not match app's.")
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
    print(answer.json)
    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    try:
    	user = userService.getUserByNameAndId(login_session['username'],login_session['email'] )
    	print("User present in database.")
    except:
    	print("User not present.Adding to database.")
    	user = User(name = data["name"],email = data["email"],picture =data["picture"])
    	eMS.save(user)

    flash("you are now logged in as %s" % login_session['username'])
    return "True"

    # DISCONNECT - Revoke a current user's token and reset their
    # login_session

@app.route('/remove/session')
def removeLoginSession():
	del login_session['access_token']
	del login_session['gplus_id']
	del login_session['username']
	del login_session['email']
	del login_session['picture']
	return "Done"

@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print('Access Token is None')
        response = make_response(json.dumps(
            'Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print('In gdisconnect access token is %s', access_token)
    print('User name is: ')
    print(login_session['username'])
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session[
        'access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print('result is ')
    print(result)
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
        print("true")
        return False
    else:
        print("false")
        return True


# Category Items
@app.route('/catalog/<path:catagory_name>/items/')
def showCategory(catagory_name):
    catagory = catagoryService.getCatagoryByName(catagory_name)
    catagory_id = catagory.id
    categories = catagoryService.getCatagoriesList()
    items = itemService.getItemsForCatagory(catagory.id)
    count = items.__len__()
    isUserLoggedIn = isLoggedIn()
    if isUserLoggedIn == True:
        print("Inside if")
        userName = login_session['username']
        userImage = login_session['picture']
        show_welcome = 'true'
    else:
        userName = ""
        userImage = ""

    return render_template('items.html', categories=categories, catagory_name=catagory_name, catagory_id=catagory_id, items=items, count=count, isLoggedIn=isUserLoggedIn, user_name=userName, user_image=userImage)

# Display a Specific Item


@app.route('/catalog/<path:catagory_name>/<path:item_id>/')
def showItem(catagory_name, item_id):
    print("TTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTT" + item_id)
    item = itemService.getItemById(item_id)
    print(item.description)
    return render_template('item.html', catagory_name=catagory_name, item=item, show_item="true")

# Add a category


@app.route('/catalog/addcategory', methods=['GET', 'POST'])
# @login_required
def addCatagory():    
    if request.method == 'POST' and isLoggedIn():
        user = userService.getUserByNameAndId(login_session['username'],login_session['email'])
        
        catagory = Catagory(name=request.form['name'],
                      user_id=user.id)

        eMS.save(catagory)
        flash('Category Successfully Created!')
        return redirect(url_for('showCatalog'))
    
    return render_template('addCatagory.html')

# Edit a category


# TODO : Edit Category not working
@app.route('/catalog/<path:catagory_name>/edit', methods=['GET', 'POST'])
# @login_required
def editCategory(catagory_name):
    print("Catagory Name : ", catagory_name)
    if isLoggedIn():
    	print ("True")
    else:
    	print ("False")
    
    catagory = catagoryService.getCatagoryByName(catagory_name)

    if request.method == 'POST' and isLoggedIn():
    	print("Inside First condition")
    	user = userService.getUserByNameAndId(login_session['username'],login_session['email'])
    	if catagory.user_id != user.id:
            flash('You do not have access to edit this item!' + user.id)
            return redirect(url_for('showCatalog'))

    	if request.form['name']:
	    	catagory.name = request.form['name']
	    	eMS.save(catagory)
	    	flash('Category Item Successfully Edited!')
	    	return redirect(url_for('showCatalog'))

    return render_template('editcategory.html',
                           catagory_name=catagory_name)
    # return

# TODO:Verify removeCategory
# Delete a category


@app.route('/catalog/<path:catagory_name>/delete', methods=['GET', 'POST'])
# @login_required
def removeCategory(catagory_name):
    catagory = catagoryService.getCatagoryByName(catagory_name)
    eMS.delete(catagory)

    categories = catagoryService.getCatagoriesList()
    items = itemService.getItemList()
    isUserLoggedIn = isLoggedIn()
    print("Is User Logged in : ", isUserLoggedIn)
    if isUserLoggedIn == True:
        print("Inside if")
        userName = login_session['username']
        userImage = login_session['picture']
    else:
        userName = ""
        userImage = ""

    return redirect(url_for('showCatalog'))


# Add an item


@app.route('/catalog/<path:catagory_name>/add', methods=['GET','POST'])
# @login_required
def addItem(catagory_name):
    if request.method == 'POST' and isLoggedIn():
        catagory = catagoryService.getCatagoryByName(catagory_name)
        user = userService.getUserByNameAndId(login_session['username'],login_session['email'])
        item = Item(name= request.form['name'],
               description= request.form['description'],
               image_url= request.form['image_url'],
               catagory_id=catagory.id,
               user_id=user.id)
        print("Saving Item")

        eMS.save(item)
        flash('Category Item Successfully Created!')
        return redirect(url_for('showCatalog'))
    

    return render_template("addItem.html",catagory_name=catagory_name)

# Edit an item


@app.route('/catalog/<path:catagory_name>/<path:item_name>/edit', methods=['GET', 'POST'])
# @login_required
def editItem(catagory_name, item_name):
    catagory = catagoryService.getCatagoryByName(catagory_name)
    item = itemService.getItemByNameAndCatagory(catagory.id, item_name)

    print("Catagory Name : ", catagory_name)
    if isLoggedIn():
        print ("True")
    else:
        print ("False")
    

    if request.method == 'POST' and isLoggedIn():
        print("Inside First condition")
        user = userService.getUserByNameAndId(login_session['username'],login_session['email'])
        if item.user_id != user.id:
            flash('You do not have access to edit this item! ')
            return redirect(url_for('showCatalog'))

        # if request.form['name']:
        print("-----------------Editing item----------------------------------")
        item.name = request.form['name']
        item.description = request.form['description']
        item.image_url = request.form['image_url']
        eMS.save(item)
        flash('Category Item Successfully Edited!')

        return redirect(url_for('showCatalog'))

    return render_template('edititem.html',
                           catagory_name=catagory_name,item=item)

# TODO:Verify removeItem
# Delete an item


@app.route('/catalog/<path:catagory_name>/<path:item_name>/delete', methods=['GET', 'POST'])
# @login_required
def removeItem(catagory_name,item_name):
    catagory = catagoryService.getCatagoryByName(catagory_name)
    item = itemService.getItemByNameAndCatagory(catagory.id, item_name)
    # item = itemService.deleteItemById(item.id)
    eMS.delete(item)
    return redirect(url_for('showCategory', catagory_name=catagory_name))


@app.route('/')
@app.route('/catalog/')
def showCatalog():
    categories = catagoryService.getCatagoriesList()
    items = itemService.getItemList()
    isUserLoggedIn = isLoggedIn()
    print("Is User Logged in : ", isUserLoggedIn)
    if isUserLoggedIn == True:
        print("Inside if")
        userName = login_session['username']
        userImage = login_session['picture']
    else:
        userName = ""
        userImage = ""

    return render_template('catagories.html', categories=categories, items=items, isLoggedIn=isUserLoggedIn, user_name=userName, user_image=userImage)

# @app.route('/catagories/<path:catagoryName>/')
# def getCatagories():
# 	categories = catagoryService.getCatagoryByName()
#     category = session.query(Category).filter_by(name=category_name).one()
#     items = session.query(Items).filter_by(category=category).order_by(asc(Items.name)).all()
#     print items
#     count = session.query(Items).filter_by(category=category).count()
#     creator = getUserInfo(category.user_id)
#     if 'username' not in login_session or creator.id != login_session['user_id']:
#         return render_template('public_items.html',category = category.name,categories = categories,items = items,
#         	count = count)
#     else:
#         user = getUserInfo(login_session['user_id'])
# return render_template('items.html',category =
# category.name,categories = categories,items = items,unt =
# count,user=user)


@app.route('/json/user')
def getAllUsers():
    users = userService.getAllUsers()
    return jsonify(users)


@app.route('/json/catagories')
def getAllCatagories():
    catagories = catagoryService.getAllCatagories()
    return jsonify(catagories)


@app.route('/json/items')
def getAllItems():
    items = itemService.getAllItems()
    return jsonify(items)

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.run(host='localhost', port=8080, debug=True)

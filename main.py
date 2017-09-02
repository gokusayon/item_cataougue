#!/usr/bin/env python

from flask import Flask, render_template, jsonify, request, flash, redirect, url_for, make_response
from database.entityManagerService import UserService,EntityManagerService
from database.database_set_up import User,Item,Catagory
from routes.item import item_routes 
from routes.catagory import catagory_routes

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

# Moved routes to seprate module
app.register_blueprint(item_routes)
app.register_blueprint(catagory_routes)

# Load secret key from file
CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Item Cataloge"

# Services for CRUD operations
eMS = EntityManagerService()
userService = UserService()

def isLoggedIn():
    access_token = login_session.get('access_token')
    if access_token is None:
        return False
    else:
        return True



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

    flash("You are now logged in as %s" % login_session['username'])
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
        return redirect(url_for('catagory.showCatalog'))
    else:
        response = make_response(json.dumps(
            'Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response

# JSON endpoints 


def has_no_empty_params(rule):
    defaults = rule.defaults if rule.defaults is not None else ()
    arguments = rule.arguments if rule.arguments is not None else ()
    return len(defaults) >= len(arguments)

# Retuns all the mapped URL's
@app.route("/site-map")
def site_map():
    links = []
    for rule in app.url_map.iter_rules():
        # Filter out rules we can't navigate to in a browser
        # and rules that require parameters
        if "GET" in rule.methods and has_no_empty_params(rule):
            url = url_for(rule.endpoint, **(rule.defaults or {}))
            links.append((url, rule.endpoint))

    return json.dumps(links)
    # links is now a list of url, endpoint tuples


# to get all users
@app.route('/user.json')
def getAllUsers():
    users = userService.getAllUsers()
    return jsonify(users)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.run(host='localhost', port=8080, debug=True)
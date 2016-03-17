from flask import Flask, render_template, request, \
    redirect, url_for, flash, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, MovieType, MovieItem, User
from flask import session as login_session
from flask import make_response
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
import requests
import random
import string
# Cliend_id from Google+ Auth API,
# client_id.json is the file in the same directroy
CLIENT_ID = json.loads(open('client_id.json', 'r').read())['web']['client_id']

# DATABASE set up
app = Flask(__name__)
engine = create_engine('sqlite:///movies.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


# Create User
def createUser(login_session):
    newUser = User(email=login_session['email'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


# get user object from id
def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


# get user id from email
def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


# Index Route
@app.route('/')
def Index():
    movieTypes = session.query(MovieType)
    newItems = session.query(MovieItem).order_by(MovieItem.id.desc()).limit(10)
    if 'email' not in login_session:
        loginAs = ""
    else:
        loginAs = login_session['email']
    return render_template('index.html', movieTypes=movieTypes,
                           newItems=newItems, loginAs=loginAs)


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    if 'email' not in login_session:
        loginAs = ""
    else:
        loginAs = login_session['email']
    return render_template('login.html', STATE=state, loginAs=loginAs)


# Show the list of movie items with type of the movie
@app.route('/movieCatagory/<movie_type_name>/')
def MovieTypes(movie_type_name):
    if 'email' not in login_session:
        loginAs = ""
    else:
        loginAs = login_session['email']
    movieTypes = session.query(MovieType)
    movieType = session.query(MovieType). \
        filter_by(name=movie_type_name).first()
    items = session.query(MovieItem).filter_by(movie_type_name=movie_type_name)
    return render_template('itemlist.html', movieTypes=movieTypes,
                           movieTypeName=movieType.name,
                           items=items, loginAs=loginAs)


# Show one movie with description
@app.route('/movieCatagory/<movie_type_name>/<movie_item_name>')
def MovieItems(movie_type_name, movie_item_name):
    if 'email' not in login_session:
        loginAs = ""
    else:
        loginAs = login_session['email']
    movieType = session.query(MovieType).filter_by(name=movie_type_name).one()
    item = session.query(MovieItem).filter_by(name=movie_item_name) \
        .first()
    if item is not None:
        return render_template('itemdescription.html',
                               item=item, loginAs=loginAs)
    else:
        return "URL error"


# Create a new Movie Item
@app.route('/movieCatagory/<movie_type_name>/new', methods=['GET', 'POST'])
def newMovieItem(movie_type_name):
    if 'email' not in login_session:
        return render_template('nopermission.html')
    else:
        movieTypes = session.query(MovieType)
        if request.method == 'POST':
            if (session.query(MovieType).filter_by(name=request.form['type']).
                    count()):
                movieType = session.query(MovieType). \
                    filter_by(name=request.form['type']).one()
                newItem = MovieItem(name=request.form['name'],
                                    movie_type_name=request.form['type'],
                                    description=request.form['description'],
                                    movie_type=movieType,
                                    user_id=login_session['user_id'])
                session.add(newItem)
                flash("New Movie \"" + request.form['name'] + "\" is added!")
                session.commit()
            return redirect(url_for('newMovieItem',
                                    movie_type_name=movie_type_name,
                                    loginAs=login_session['email']))
        else:
            return render_template('newmovieitem.html', newItem="",
                                   movieTypes=movieTypes,
                                   movie_type_name=movie_type_name,
                                   loginAs=login_session['email'])


# edit movie item name and movie item description
@app.route('/movieCatagory/<movie_type_name>/<movie_item_name>/edit/',
           methods=['GET', 'POST'])
def editMovieItem(movie_type_name, movie_item_name):
    if 'email' not in login_session:
        return render_template('nopermission.html')
    else:
        editedItem = session.query(MovieItem). \
            filter_by(movie_type_name=movie_type_name,
                      name=movie_item_name).first()
        if ('user_id' not in login_session or
                editedItem.user_id != login_session['user_id']):
            return render_template('nopermission.html')

        elif request.method == 'POST':
            if request.form['name']:
                editedItem.name = request.form['name']
                editedItem.description = request.form['description']
                flash("\"" + request.form['name'] + "\" is edited!")
                session.add(editedItem)
                session.commit()
            return redirect(url_for('MovieItems',
                            movie_type_name=movie_type_name,
                            movie_item_name=editedItem.name,
                            loginAs=login_session['email']))
        else:
            return render_template('editMovieItem.html',
                                   movie_type_name=movie_type_name,
                                   movie_item_name=movie_item_name,
                                   item=editedItem,
                                   loginAs=login_session['email'])


# delete movie item
@app.route('/movieCatagory/<movie_type_name>/<movie_item_name>/delete/',
           methods=['GET', 'POST'])
def deleteMovieItem(movie_type_name, movie_item_name):
    if 'email' not in login_session:
        return render_template('nopermission.html')
    else:
        itemToDelete = session.query(MovieItem). \
            filter_by(movie_type_name=movie_type_name,
                      name=movie_item_name).first()
        if ('user_id' not in login_session or
                itemToDelete.user_id != login_session['user_id']):
            return render_template('nopermission.html')
        elif request.method == 'POST':
            session.delete(itemToDelete)
            session.commit()
            flash("Movie is deleted!")
            return redirect(url_for('MovieTypes',
                                    movie_type_name=movie_type_name))


# Making an API Endpoint (GET request)
@app.route('/movieCatagory/<movie_type_name>/JSON')
def movieJSON(movie_type_name):
    items = session.query(MovieItem). \
        filter_by(movie_type_name=movie_type_name).all()
    return jsonify(MovieItems=[i.serialize for i in items])


# google Auth Code,  By Udacity OAuth Course
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_id.json', scope='')
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
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response
    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if (stored_access_token is not None and
            gplus_id == stored_gplus_id):
        response = make_response(json.dumps('Current user already connected.'),
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
    # Create User and store in database
    # Identify the user who logged in
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['email']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px; \
               border-radius: 150px;-webkit-border-radius: \
               150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['email'])
    return output


# DISCONNECT - Revoke a current user's token and reset their login_session,
# By Udacity OAuth Course
@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session['access_token']
    print 'In gdisconnect access token is %s', access_token
    print 'User name is:'
    print login_session['username']
    if access_token is None:
        print 'Access Token is None'
        response = make_response(json.dumps('User not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' \
        % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)

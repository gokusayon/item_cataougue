# item_cataougue
FSND: Udacity Project 5 !

## This project includes:
- main.py
- database/**  	[Files for setting up database and working CRUD]
- static/**		[CSS files]
- templates		[html templates]

## To Run


## Setup

###Google Plus Authentication.
1. Go to https://console.developers.google.com/project and login.
2. Create a new project with name 'item_catalog'.
3. Go to Auth -> Credentials and create 'OAuth Client Id'
4. Select 'Web Application' and add
		-http://localhost:8080/
		to origins and redirect Url
5. Download JSON and rename to client_secrets.json

###Running the application

#### You will need:
- python3/python2
- Vagrant
- VirtualBox
- MySql Server 5.5 or above

1. Install following dependencies using pip or easy_install
	-flask
	-sqlalchemy
	-oauth2client
2. Set up the user and database(item_catalog) using following commands
	- `mysql -u <user> -p <password> item_catalog < item_catalog.sql`
	- Go to database and run `python database_init.py`

Alternatively you can use Vagrant and Virtual Box. 

To execute the program, run `python3 main.py` from the command line.

## Author
**Vasu Sheoran**

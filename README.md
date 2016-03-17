## Item Catalog -- Movie APP

Udacity Nanodegree: Full Stack (Project 3)


## Usage

Before you begin ensure you have the following installed:

* [VirtualBox](https://www.virtualbox.org/)
* [Vagrant](https://www.vagrantup.com/)


### Clone & start the virtual machine

1. put your catalog folder under your vagrant catalog
2.  `vagrant up`
3.  `vagrant ssh`

### Move to the correct directory

1. `cd /vagrant/catalog`
2. run `python database_setup.py` to set up database schema
3. run `python data.py` to import initial data

	
### Run app

 1.  run `python project.py`
 2.  open brower and put the url
 		`http://localhost:5000`
 3.  without logging in, you can see all the default items but can't edit or delete
 4.  sign in use your google account.

#### CREATE
   To create item you have to login, click the add item button at `http://localhost:5000/movieCatagory/Action/`, The item you created will show in the main page of latest movie section(click the Logo on the top left corner redirect to the main page), also you can find it in the right catagory.
#### UPDATE
   click the name of the movie and find the edit button(have to login, only be able to edit if you have the ownership of the item)

#### DELETE
	Same as update, but you click the delete button
#### JSON API
    URL 
    http://localhost:5000/movieCatagory/<MovieType>/JSON
    For example:
     http://localhost:5000/movieCatagory/Action/JSON



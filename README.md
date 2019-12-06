# team_assignment_3

Final semester project for CMSC435 Fall 2019.

* Milestone 2 commit: 8cf84440863541b334df589a171f70dc91bfbc1c

## Developer Documentation

*Software architecture*: Code is store in the flaskapp directory, 
	web design is inside the teamplates directory under the same directory.

__init__.py: Initialize the database and the app

forms.py: The Form used in the app, including Registraion, Login, 
         Update Profile, Search (user and project), Create Project.  

modelts.py: The format for the User, Project, Project members,
         Project message, Project images database.  





## Running the application (Docker)

*Note*: These steps assume you have docker and docker-compose installed.

Run the app with ```docker-compose```

    $ docker-compose up

To rebuild the application before running

    $ docker-compose up --build

## Installing the application (Local only)

1. Create your virtual environment.

- For virtualenv:

        $ python3 -m venv venv
        $ source venv/bin/activate

2. Install the application requirements with pip:

        $ pip install -r requirements.txt

## Running the application (Local only)

To run the application in development mode:

    $ python run.py

- Please post a message on Slack if any of these steps still cause errors.

- Note: I added a .flaskenv file to the project, so there is no need to set
  FLASK_APP and FLASK_ENV.


## Updating the requirements.txt file

After using pip to install some new dependencies on your local environment, the
requirements.txt file needs to be updated before you commit your code, or your
changes might cause the application to break on someone else's machine.

This is how you do it:

    $ pip freeze > requirements.txt

This will update the requirements.txt file with the new dependencies. 

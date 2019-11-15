from datetime import datetime
from flaskapp import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    description = db.Column(db.String(1000), nullable=True)
    business=db.Column(db.Boolean,default=False)
    technology=db.Column(db.Boolean,default=False)
    art=db.Column(db.Boolean,default=False)
    music=db.Column(db.Boolean,default=False)
    literature=db.Column(db.Boolean,default=False)
    projects = db.relationship('Project', backref='author', lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"



class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False)
    business = db.Column(db.Boolean, default=False)
    technology = db.Column(db.Boolean, default=False)
    art = db.Column(db.Boolean, default=False)
    music = db.Column(db.Boolean, default=False)
    literature = db.Column(db.Boolean, default=False)


    def __repr__(self):
        return f"Project('{self.title}', '{self.date_posted}', '{self.id}', '{self.user_id}')"

#   THESE TABLES ARE USED TO STORE THE PROJECTS AND USERS THAT CORRESPOND TO A CERTAIN TAG
#   THE PREDEFINED TAGS ARE Business, Literature, Technology, Art, Music
#   THE TITLE COLUMN IS EITHER "PROJECT" OR "USER" AND THE ID COLUMN IS THE ID OF THE PROJECT/USER
#   THESE TABLES CAN COME IN HANDY WHEN SEARCHING FOR PROJECTS/USERS BASED ON TAGS


class Business(db.Model):
    type = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100), primary_key=True, unique=True, nullable=False)

    def __repr__(self):
        return f"Business('{self.type}', '{self.name}')"


class Literature(db.Model):
    type = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100), primary_key=True, unique=True, nullable=False)

    def __repr__(self):
        return f"Literature('{self.type}', '{self.name}')"


class Technology(db.Model):
    type = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100), primary_key=True, unique=True, nullable=False)

    def __repr__(self):
        return f"Technology('{self.type}', '{self.name}')"


class Art(db.Model):
    type = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100), primary_key=True, unique=True, nullable=False)

    def __repr__(self):
        return f"Art('{self.type}', '{self.name}')"


class Music(db.Model):
    type = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100), primary_key=True, unique=True, nullable=False)

    def __repr__(self):
        return f"Music('{self.type}', '{self.name}')"


class ProjectMembers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    project_id = db.Column(db.Integer,db.ForeignKey('project.id'), nullable=False)

    def __repr__(self):
        return f"ProjectMembers('{self.user_id}', '{self.user_id}', '{self.project_id}')"


class ProjectMessages(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    project_id = db.Column(db.Integer,db.ForeignKey('project.id'), nullable=False)
    message = db.Column(db.String(1000), nullable=True)

    def __repr__(self):
        return f"ProjectMessages('{self.user_id}', '{self.project_id}')"

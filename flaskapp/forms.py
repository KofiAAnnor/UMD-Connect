from flask_wtf import FlaskForm
from flaskapp.models import User
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError,Optional


class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')


class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class UpdateForm(FlaskForm):
    username = StringField('New Username',
                           validators=[Length(min=2,max=20),Optional()])
    new_email = StringField('New Email',
                        validators=[Email(),Optional()])
    skills_bus = BooleanField('Business')
    skills_lit = BooleanField('Literature')
    skills_tech=BooleanField('Technology')
    skills_art=BooleanField('Art')
    skills_music=BooleanField('Music')
    new_password = PasswordField('New Password')
    confirm_new_password = PasswordField('Confirm New Password',
                                     validators=[EqualTo('new_password')])
    old_password = PasswordField('Enter Password to Update',validators=[DataRequired()])
    submit = SubmitField('Update')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_new_email(self, new_email):
        user = User.query.filter_by(email=new_email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')

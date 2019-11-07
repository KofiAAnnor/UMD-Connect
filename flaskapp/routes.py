from flask import render_template, url_for, flash, redirect, request
from flaskapp import app, db, bcrypt
from flaskapp.forms import RegistrationForm, LoginForm,UpdateForm
from flaskapp.models import User, Project, Business, Technology, Literature, Art, Music
from flask_login import login_user, current_user, logout_user, login_required


@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html', title="Home")


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()

        flash(f'Your account has been created! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html', title="Register", form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email/password', 'danger')

    return render_template('login.html', title="Login", form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route("/profile")
@login_required
def profile():
    user = User.query.filter_by(email=current_user.email).first()
    tags = {
        "BusinessTag": Business.query.filter_by(name=user.username).first(),
        "LiteratureTag": Literature.query.filter_by(name=user.username).first(),
        "TechnologyTag":  Technology.query.filter_by(name=user.username).first(),
        "ArtTag":  Art.query.filter_by(name=user.username).first(),
        "MusicTag":  Music.query.filter_by(name=user.username).first(),
    }
    return render_template('profile.html', title='Profile', skillTags=tags)


@app.route("/delete_account",methods=["POST"])
@login_required
def delete_account():
    user=User.query.filter_by(email=request.form['email']).first()
    db.session.delete(user)
    db.session.commit()
    return logout()

@app.route("/update",methods=["POST",'GET'])
@login_required
def update():
    form=UpdateForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=current_user.email).first()
        if bcrypt.check_password_hash(user.password, form.old_password.data):
            if form.new_email.data :
                user.email=form.new_email.data
            if form.username.data:
                user.username=form.username.data
            if form.skills.data:
                user.skills = form.skills.data
            if form.new_password.data:
                hashed_password = bcrypt.generate_password_hash(form.new_password.data).decode('utf-8')
                user.password = hashed_password
            db.session.commit()
            flash(f'Your account has been updated.', 'success')
            return redirect(url_for('profile'))
        else:
            flash('Incorrect. Please check password', 'danger')
    return render_template('update.html', title='Update',form=form)


@app.route("/project-board")
def project_board_page():
    return render_template('project-board.html', title='Project Board')


@app.route("/project-detail")
def project_detail_view():
    return render_template('project-detail-view.html', title='Project Detail')

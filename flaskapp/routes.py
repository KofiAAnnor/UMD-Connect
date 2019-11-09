from flask import render_template, url_for, flash, redirect, request, abort
from flaskapp import app, db, bcrypt
from flaskapp.forms import RegistrationForm, LoginForm, UpdateForm, NewProjectForm
from flaskapp.models import User, Project, Business, Technology, Literature, Art, Music
from flask_login import login_user, current_user, logout_user, login_required


@app.route("/")
@app.route("/home")
@login_required
def home():
    your_projects = Project.query.filter_by(user_id=current_user.id)\
                    .order_by(Project.date_posted.desc()).limit(3).all()
    projects = Project.query.filter(Project.user_id != current_user.id)\
                    .order_by(Project.date_posted.desc()).limit(6).all()
    return render_template('home.html', title="Home", projects=projects, your_projects=your_projects)


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
            flash('Login Unsuccessful. Please check email/password and try again.', 'danger')

    return render_template('login.html', title="Login", form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route("/user/<string:username>/profile")
@login_required
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    image_file = url_for('static', filename='profile_pics/' + user.image_file)
    tags = {
        "BusinessTag": Business.query.filter_by(name=user.username).first(),
        "LiteratureTag": Literature.query.filter_by(name=user.username).first(),
        "TechnologyTag": Technology.query.filter_by(name=user.username).first(),
        "ArtTag": Art.query.filter_by(name=user.username).first(),
        "MusicTag": Music.query.filter_by(name=user.username).first(),
    }

    return render_template('profile.html', title=user.username+'\'s Profile',
                            user=user, skillTags=tags, image_file=image_file)


@app.route("/delete_account", methods=["POST"])
@login_required
def delete_account():
    user = User.query.filter_by(email=request.form['email']).first()
    db.session.delete(user)
    db.session.commit()
    return logout()


@app.route("/update_profile", methods=["POST", 'GET'])
@login_required
def update_profile():
    form = UpdateForm()
    bus = Business.query.filter_by(name=current_user.username, type="user").first()
    tec = Technology.query.filter_by(name=current_user.username, type="user").first()
    lit = Literature.query.filter_by(name=current_user.username, type="user").first()
    mu = Music.query.filter_by(name=current_user.username, type="user").first()
    ar = Art.query.filter_by(name=current_user.username, type="user").first()

    if form.validate_on_submit():
        user = User.query.filter_by(email=current_user.email).first()
        if bcrypt.check_password_hash(user.password, form.old_password.data):
            if form.new_email.data:
                user.email = form.new_email.data
            if form.username.data:
                user.username = form.username.data
            if form.description.data:
                user.description = form.description.data

            if form.skills_bus.data and not bus:
                b = Business(name=user.username, type="user")
                db.session.add(b)
            elif not form.skills_bus.data and bus:
                db.session.delete(bus)
            if form.skills_lit.data and not lit:
                b = Literature(name=user.username, type="user")
                db.session.add(b)
            elif not form.skills_lit.data and lit:
                db.session.delete(lit)
            if form.skills_tech.data and not tec:
                b = Technology(name=user.username, type="user")
                db.session.add(b)
            elif not form.skills_tech.data and tec:
                db.session.delete(tec)
            if form.skills_art.data and not ar:
                b = Art(name=user.username, type="user")
                db.session.add(b)
            elif not form.skills_art.data and ar:
                db.session.delete(ar)
            if form.skills_music.data and not mu:
                b = Music(name=user.username, type="user")
                db.session.add(b)
            elif not form.skills_music.data and mu:
                db.session.delete(mu)

            if form.new_password.data:
                hashed_password = bcrypt.generate_password_hash(form.new_password.data).decode('utf-8')
                user.password = hashed_password

            db.session.commit()
            flash(f'Your account has been updated.', 'success')
            return redirect(url_for('profile'))
        else:
            flash('Incorrect. Please check password', 'danger')
    return render_template('update-profile.html', title='Update Profile', form=form,
                            bus=bus, tec=tec, mu=mu, art=ar, lit=lit)


@app.route("/user/<string:username>/project_board")
@login_required
def project_board(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    projects = Project.query.filter_by(user_id=current_user.id).paginate(page=page, per_page=6)

    return render_template('project-board.html', title='Project Board', user=user, projects=projects)


@app.route("/explore")
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    projects = Project.query.filter(Project.user_id != current_user.id)\
                            .paginate(page=page, per_page=6)

    return render_template('explore.html', title="Explore", projects=projects)


@app.route("/project/new", methods=['GET', 'POST'])
@login_required
def new_project():
    form = NewProjectForm()
    if form.validate_on_submit():
        project = Project(title=form.title.data, description=form.description.data,
                            author=current_user)
        db.session.add(project)
        db.session.commit()
        flash('Your project has been created!', 'success')

        return redirect(url_for('project_detail_view', project_id=project.id))
    return render_template('project.html', title='New Project', form=form,
                                legend='New Project')


@app.route("/project/<int:project_id>")
@login_required
def project_detail_view(project_id):
    project = Project.query.get_or_404(project_id)
    return render_template('project-detail-view.html', title='Project Detail', project=project)


@app.route("/project/<int:project_id>/update", methods=['GET', 'POST'])
@login_required
def update_project(project_id):
    project = Project.query.get_or_404(project_id)
    if project.author != current_user:
        abort(403)
    form = NewProjectForm()
    if form.validate_on_submit():
        project.title = form.title.data
        project.description = form.description.data
        db.session.commit()
        flash('Your project has been updated!', 'success')
        return redirect(url_for('project_detail_view', project_id=project.id))
    elif request.method == 'GET':
        form.title.data = project.title
        form.description.data = project.description

    return render_template('project.html', title='Update Project', form=form,
                            legend='Update Project')


@app.route("/project/<int:project_id>/delete", methods=['POST'])
@login_required
def delete_project(project_id):
    project = Project.query.get_or_404(project_id)
    if project.author != current_user:
        abort(403)
    db.session.delete(project)
    db.session.commit()
    flash('Project '+ project.title +' has been deleted!', 'success')

    return redirect(url_for('home'))

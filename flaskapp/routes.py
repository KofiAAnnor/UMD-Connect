from flask import render_template, url_for, flash, redirect, request
from flaskapp import app, db, bcrypt
from flaskapp.forms import RegistrationForm, LoginForm, UpdateForm
from flaskapp.models import User, Project, Business, Technology, Literature, Art, Music, ProjectMembers
from flask_login import login_user, current_user, logout_user, login_required


@app.route("/")
@app.route("/home")
@login_required
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
            flash('Login Unsuccessful. Please check email/password and try again.', 'danger')

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
        "BusinessTag": User.query.filter_by(business=True, username=user.username).first(),
        "LiteratureTag": User.query.filter_by(literature=True, username=user.username).first(),
        "TechnologyTag": User.query.filter_by(technology=True, username=user.username).first(),
        "ArtTag": User.query.filter_by(art=True, username=user.username).first(),
        "MusicTag": User.query.filter_by(music=True, username=user.username).first(),
    }
    user_personal_projects = []
    user_collab_projects = []
    all_users_projects = ProjectMembers.query.filter_by(user_id=current_user.get_id()).all()
    for proj in all_users_projects:
        proj_id = proj.project_id
        user_project = Project.query.filter_by(id=proj_id).first()
        if str(user_project.user_id) == str(current_user.get_id()):
            user_personal_projects.append(user_project)
        else:
            user_collab_projects.append(user_project)
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    flash(user_personal_projects)
    flash(user_collab_projects)
    return render_template('profile.html', title='Profile', skillTags=tags, image_file=image_file, personal_projects=user_personal_projects, collab_projects=user_collab_projects)


@app.route("/delete_account", methods=["POST"])
@login_required
def delete_account():
    user = User.query.filter_by(email=request.form['email']).first()
    db.session.delete(user)
    db.session.commit()
    return logout()


@app.route("/update", methods=["POST", 'GET'])
@login_required
def update():
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
            if form.skills_bus.data and not current_user.business:
                # b = Business(name=user.username, type="user")
                # db.session.add(b)
                current_user.business = True
            elif not form.skills_bus.data and current_user.business:
                # db.session.delete(bus)
                current_user.business = False
            if form.skills_lit.data and not current_user.literature:
                # b = Literature(name=user.username, type="user")
                # db.session.add(b)
                current_user.literature = True
            elif not form.skills_lit.data and current_user.literature:
                # db.session.delete(lit)
                current_user.literature = False
            if form.skills_tech.data and not current_user.technology:
                # b = Technology(name=user.username, type="user")
                # db.session.add(b)
                current_user.technology = True
            elif not form.skills_tech.data and current_user.technology:
                # db.session.delete(tec)
                current_user.technology = False
            if form.skills_art.data and not current_user.art:
                # b = Art(name=user.username, type="user")
                # db.session.add(b)
                current_user.art = True
            elif not form.skills_art.data and current_user.art:
                # db.session.delete(ar)
                current_user.art = False
            if form.skills_music.data and not current_user.music:
                # b = Music(name=user.username, type="user")
                # db.session.add(b)
                current_user.music = True
            elif not form.skills_music.data and current_user.music:
                # db.session.delete(mu)
                current_user.music = False
            if form.new_password.data:
                hashed_password = bcrypt.generate_password_hash(form.new_password.data).decode('utf-8')
                user.password = hashed_password

            db.session.commit()
            flash(f'Your account has been updated.', 'success')
            return redirect(url_for('profile'))
        else:
            flash('Incorrect. Please check password', 'danger')

    return render_template('update.html', title='Update', form=form, bus=bus, tec=tec, mu=mu, art=ar, lit=lit)


@app.route("/project-board")
def project_board_page():
    return render_template('project-board.html', title='Project Board')



@app.route("/project-detail" , methods=["POST", 'GET'])
@login_required
def project_detail_view():
    if request.method == 'POST':
        image_file = url_for('static', filename='profile_pics/project-default-image.jpg')
        proj = Project.query.filter_by(id=request.form["projectId"]).first()
        members_query= ProjectMembers.query.filter_by(project_id=request.form["projectId"])
        user = User.query.filter_by(id=proj.user_id).first()
        project_members = []
        for x in members_query:
            name = User.query.filter_by(id=x.user_id).first().username
            project_members.append(name)
        if request.form['submit_button'] == "View":
            return render_template('project-detail-view.html', title='Project Detail', project=proj, image_file=image_file, members=project_members, user=user)
    else:
        return redirect(url_for('profile'))


@app.route("/add-project" , methods=["POST", 'GET'])
@login_required
def add_project():
    if request.method == 'POST':
        project_name = request.form['ProjectName']
        project_description = request.form['ProjectDescription']
        project_status = request.form.get('projectStatus')
        if project_status is not None:
            project = Project(title=project_name, content=project_description, user_id=current_user.get_id(), status="open")
        else:
            project = Project(title=project_name, content=project_description, user_id=current_user.get_id(), status="closed")
        if request.form.get('business') is not None:
            project.business = True;
        if request.form.get('technology') is not None:
            project.technology = True;
        if request.form.get('music') is not None:
            project.music = True;
        if request.form.get('art') is not None:
            project.art = True;
        if request.form.get('literature') is not None:
            project.literature = True;
        db.session.add(project)
        db.session.commit()

        memberEntry = ProjectMembers(user_id=current_user.get_id(), project_id=project.id)
        db.session.add(memberEntry)
        db.session.commit()

        flash(f'Your project has been added.', 'success')
        return redirect(url_for('profile'))
    return render_template('add-project.html', title='Profile')


@app.route("/update-project", methods=["POST", 'GET'])
@login_required
def update_project():
    if request.form['submit_button'] == "Edit":
        proj = Project.query.filter_by(id=request.form["projectId"]).first()
        return render_template('update-project.html', title='Edit Project', project=proj)
    elif request.form['submit_button'] == "edit_project":
        proj = Project.query.filter_by(id=request.form["projectId"]).first()
        proj.title = request.form['ProjectName']
        proj.content = request.form['ProjectDescription']
        project_status = request.form.get('projectStatus')
        if project_status is not None:
            proj.status = "open"
        else:
            proj.status = "closed"

        if request.form.get('business') is not None:
            proj.business = True;
        else:
            proj.business = False;

        if request.form.get('technology') is not None:
            proj.technology = True;
        else:
            proj.technology = False;

        if request.form.get('music') is not None:
            proj.music = True;
        else:
            proj.music = False;

        if request.form.get('art') is not None:
            proj.art = True;
        else:
            proj.art = False;

        if request.form.get('literature') is not None:
            proj.literature = True;
        else:
            proj.literature = False;
        db.session.commit()
        flash(f'Your project has been updated.', 'success')
        proj = Project.query.filter_by(id=request.form['projectId']).first()
    return redirect(url_for('profile'))


@app.route("/add-project-members" , methods=["POST", 'GET'])
@login_required
def add_project_members():
    if request.form['submit_button'] == "Add":
        memberId = User.query.filter_by(username=request.form["MemberName"]).first()
        if memberId is None:
            flash("User Doesnt Exist")
            return redirect(url_for('profile'))
        proj_member = ProjectMembers.query.filter_by(user_id=memberId.id, project_id=request.form["projectId"]).first()
        if proj_member is not None:
            flash("User Already Member")
            return redirect(url_for('profile'))
        memberEntry = ProjectMembers(user_id=memberId.id, project_id=request.form["projectId"])
        db.session.add(memberEntry)
        db.session.commit()
        flash(f'Member has been added.', 'success')
        return redirect(url_for('profile'))
    else:
        return render_template('add-project-members.html', title='Profile', id=request.form["projectId"])

@app.route("/restricted-profile-view" , methods=["POST", 'GET'])
@login_required
def restricted_profile():
    unames = request.form["submit_button"]
    flash(unames)
    if current_user.username == unames:
        return redirect(url_for('profile'))
    user = User.query.filter_by(username=unames).first()
    tags = {
        "BusinessTag": User.query.filter_by(business=True, username=user.username).first(),
        "LiteratureTag": User.query.filter_by(literature=True, username=user.username).first(),
        "TechnologyTag": User.query.filter_by(technology=True, username=user.username).first(),
        "ArtTag": User.query.filter_by(art=True, username=user.username).first(),
        "MusicTag": User.query.filter_by(music=True, username=user.username).first(),
    }

    user_personal_projects = []
    user_collab_projects = []
    all_users_projects = ProjectMembers.query.filter_by(user_id=user.id).all()
    for proj in all_users_projects:
        proj_id = proj.project_id
        user_project = Project.query.filter_by(id=proj_id).first()
        if str(user_project.user_id) == str(user.id):
            user_personal_projects.append(user_project)
        else:
            user_collab_projects.append(user_project)
    image_file = url_for('static', filename='profile_pics/' + user.image_file)
    return render_template('restricted-profile-view.html', user=user, title='Profile', skillTags=tags, image_file=image_file, personal_projects=user_personal_projects, collab_projects=user_collab_projects)

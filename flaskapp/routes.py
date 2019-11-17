import os
import secrets
from flask import render_template, url_for, flash, redirect, request, abort
from flaskapp import app, db, bcrypt
from flaskapp.forms import RegistrationForm, LoginForm, UpdateForm, SearchForm, NewProjectForm
from flaskapp.models import User, Project, ProjectMembers, ProjectImages
from flask_login import login_user, current_user, logout_user, login_required
from PIL import Image

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

        flash(f'Your account has been created!', 'success')
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
    user_personal_projects = []
    user_collab_projects = []
    all_users_projects = ProjectMembers.query.filter_by(user_id=user.id).all()

    for proj in all_users_projects:
        proj_id = proj.project_id
        user_project = Project.query.filter_by(id=proj_id).first()
        if username == current_user.username:
            if str(user_project.user_id) == str(current_user.get_id()):
                user_personal_projects.append(user_project)
            else:
                user_collab_projects.append(user_project)
        else:
            if str(user_project.user_id) == str(current_user.get_id()):
                user_collab_projects.append(user_project)
            else:
                user_personal_projects.append(user_project)
    return render_template('profile.html', title=user.username+'\'s Profile',
                            user=user, image_file=image_file , personal_projects=user_personal_projects,
                           collab_projects=user_collab_projects)


@app.route("/delete_account", methods=["POST"])
@login_required
def delete_account():
    user = User.query.filter_by(email=request.form['email']).first()
    db.session.delete(user)
    db.session.commit()
    return logout()


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (250, 250)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


@app.route("/user/update_profile", methods=["POST", 'GET'])
@login_required
def update_profile():
    form = UpdateForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=current_user.email).first()
        if bcrypt.check_password_hash(user.password, form.old_password.data):
            if form.new_email.data:
                user.email = form.new_email.data
            if form.username.data:
                user.username = form.username.data
            if form.description.data:
                user.description = form.description.data
            if form.picture.data:
                picture_file = save_picture(form.picture.data)
                current_user.image_file = picture_file
            if form.skills_bus.data and not current_user.business:
                current_user.business=True
            elif not form.skills_bus.data and current_user.business:
                current_user.business = False
            if form.skills_lit.data and not current_user.literature:
                current_user.literature = True
            elif not form.skills_lit.data and current_user.literature:
                current_user.literature = False
            if form.skills_tech.data and not current_user.technology:
                current_user.technology=True
            elif not form.skills_tech.data and current_user.technology:
                current_user.technology=False
            if form.skills_art.data and not current_user.art:
                current_user.art=True
            elif not form.skills_art.data and current_user.art:
                current_user.art=False
            if form.skills_music.data and not current_user.music:
                current_user.music=True
            elif not form.skills_music.data and current_user.music:
                current_user.music=False
            if form.new_password.data:
                hashed_password = bcrypt.generate_password_hash(form.new_password.data).decode('utf-8')
                user.password = hashed_password

            db.session.commit()
            flash(f'Your account has been updated.', 'success')
            return redirect(url_for('profile', username=current_user.username))
        else:
            flash('Incorrect. Please check password', 'danger')
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('update-profile.html', title='Update Profile', form=form, image_file=image_file)



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

        flash('Your project has been created!', 'success')

        return redirect(url_for('project_detail_view', project_id=project.id))
    return render_template('project.html', title='New Project', form=form,
                                legend='New Project')


@app.route("/project/<int:project_id>")
@login_required
def project_detail_view(project_id):
    project = Project.query.get_or_404(project_id)
    members_query = ProjectMembers.query.filter_by(project_id=project_id)
    user = User.query.filter_by(id=project.user_id).first()
    project_members = []
    for x in members_query:
        name = User.query.filter_by(id=x.user_id).first().username
        project_members.append(name)
    project_image_gallery = []
    gallery_images = ProjectImages.query.filter_by(project_id=project_id)
    if gallery_images is not None:
        for images in gallery_images:
            project_image_gallery.append(url_for('static', filename='profile_pics/' + images.image_file))

    return render_template('project-detail-view.html', title='Project Detail', project=project, members=project_members, user=user,
                           project_image_gallery=project_image_gallery)


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

        project_status = request.form.get('projectStatus')
        if project_status is not None: project.status = "open"
        else: project.status = "closed"
        if request.form.get('business') is not None: project.business = True;
        else: project.business = False;
        if request.form.get('technology') is not None: project.technology = True;
        else: project.technology = False;
        if request.form.get('music') is not None: project.music = True;
        else: project.music = False;
        if request.form.get('art') is not None: project.art = True;
        else: project.art = False;
        if request.form.get('literature') is not None: project.literature = True;
        else: project.literature = False;

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


@app.route("/search", methods=["POST", 'GET'])
@login_required
def search():
    form=SearchForm()
    if form.is_submitted():
        if form.name.data:
            if form.type.data=="User":
                user=User.query.filter_by(username=form.name.data).first()
                if form.type.data=="User" and user:
                    return render_template('search.html', title='Search', form=form,user={user})
            else:
                project=Project.query.filter_by(title=form.name.data).first()
                if project:
                    return render_template('search.html', title='Search', form=form, projects={project})
        elif form.skills_tech.data or form.skills_lit.data or form.skills_art.data or \
                form.skills_bus.data or form.skills_music.data:
            if form.type.data=="User":
                users=[]
                if form.skills_bus.data:
                    u=User.query.filter_by(business=form.skills_bus.data).all()
                    for us in u:
                        users.append(us)
                if form.skills_tech.data:
                    u=User.query.filter_by(technology=form.skills_tech.data).all()
                    for us in u:
                        if us not in users:
                            users.append(us)
                if form.skills_lit.data:
                    u=User.query.filter_by(literature=form.skills_lit.data).all()
                    for us in u:
                        if us not in users:
                            users.append(us)
                if form.skills_art.data:
                    u=User.query.filter_by(art=form.skills_art.data).all()
                    for us in u:
                        if us not in users:
                            users.append(us)
                if form.skills_music.data:
                    u = User.query.filter_by(music=form.skills_music.data).all()
                    for us in u:
                        if us not in users:
                            users.append(us)
                return render_template('search.html',title='Search',form=form,user=users)
            else: #projects has no skill field yet
                projects=[]
                return render_template('search.html', title='Search', form=form, projects=projects)

    return render_template('search.html', title='Search', form=form)

@app.route("/add-project-members" , methods=["POST", 'GET'])
@login_required
def add_project_members():
    if request.form['submit_button'] == "Add":
        memberId = User.query.filter_by(username=request.form["MemberName"]).first()
        if memberId is None:
            flash("User Doesnt Exist")
            return redirect(url_for('profile', username = current_user.username))
        proj_member = ProjectMembers.query.filter_by(user_id=memberId.id, project_id=request.form["projectId"]).first()
        if proj_member is not None:
            flash("User Already Member")
            return redirect(url_for('profile', username = current_user.username))
        memberEntry = ProjectMembers(user_id=memberId.id, project_id=request.form["projectId"])
        db.session.add(memberEntry)
        db.session.commit()
        flash(f'Member has been added.', 'success')
        return redirect(url_for('profile', username = current_user.username))
    else:
        return render_template('add-project-members.html', title='Profile', id=request.form["projectId"])


@app.route("/user/add-project-gallery-image", methods=["POST", 'GET'])
@login_required
def add_project_image():
    form = UpdateForm()
    user = User.query.filter_by(email=current_user.email).first()
    if form.picture.data:
        picture_file = save_picture(form.picture.data)
        image_entry = ProjectImages(image_file=picture_file, project_id=request.form["projectId"])
        db.session.add(image_entry)
        db.session.commit()
        flash(f'Image has been added.', 'success')
        return redirect(url_for('profile', username=current_user.username))

    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('add-project-gallery-image.html', title='Update Profile', form=form, image_file=image_file, id=request.form["projectId"])

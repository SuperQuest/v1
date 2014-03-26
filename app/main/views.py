from flask import render_template, redirect, url_for, abort, flash, request,\
    current_app, make_response
from flask.ext.login import login_required, current_user
from flask.ext.sqlalchemy import get_debug_queries
from . import main
from .forms import EditProfileForm, EditProfileAdminForm, PostForm,\
    CommentForm, ProjectForm, SearchForm
from .. import db
from ..models import Permission, Role, User, Post, Comment, Project
from ..decorators import admin_required, permission_required


@main.after_app_request
def after_request(response):
    for query in get_debug_queries():
        if query.duration >= current_app.config['FLASKY_SLOW_DB_QUERY_TIME']:
            current_app.logger.warning(
                'Slow query: %s\nParameters: %s\nDuration: %fs\nContext: %s\n'
                % (query.statement, query.parameters, query.duration,
                   query.context))
    return response


@main.route('/shutdown')
def server_shutdown():
    if not current_app.testing:
        abort(404)
    shutdown = request.environ.get('werkzeug.server.shutdown')
    if not shutdown:
        abort(500)
    shutdown()
    return 'Shutting down...'


# @main.route('/posts', methods=['GET', 'POST'])
# def index():
#     form = PostForm()
#     if current_user.can(Permission.WRITE_ARTICLES) and \
#             form.validate_on_submit():
#         post = Post(body=form.body.data,
#                     author=current_user._get_current_object())
#         db.session.add(post)
#         return redirect(url_for('.index'))
#     page = request.args.get('page', 1, type=int)
#     show_followed = False
#     if current_user.is_authenticated():
#         show_followed = bool(request.cookies.get('show_followed', ''))
#     if show_followed:
#         query = current_user.followed_posts
#     else:
#         query = Post.query
#     pagination = query.order_by(Post.timestamp.desc()).paginate(
#         page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
#         error_out=False)
#     posts = pagination.items
#     return render_template('index.html', form=form, posts=posts,
#                            show_followed=show_followed, pagination=pagination)


@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    pagination = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    return render_template('user.html', user=user, posts=posts,
                           pagination=pagination)


@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        flash('Your profile has been updated.')
        return redirect(url_for('.user', username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)


@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(current_user)
        flash('The profile has been updated.')
        return redirect(url_for('.user', username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('edit_profile.html', form=form, user=user)


@main.route('/post/<int:id>', methods=['GET', 'POST'])
def post(id):
    post = Post.query.get_or_404(id)
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(body=form.body.data,
                          post=post,
                          author=current_user._get_current_object())
        db.session.add(comment)
        flash('Your comment has been published.')
        return redirect(url_for('.post', id=post.id, page=-1))
    page = request.args.get('page', 1, type=int)
    if page == -1:
        page = (post.comments.count() - 1) / \
            current_app.config['FLASKY_COMMENTS_PER_PAGE'] + 1
    pagination = post.comments.order_by(Comment.timestamp.asc()).paginate(
        page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'],
        error_out=False)
    comments = pagination.items
    return render_template('post.html', posts=[post], form=form,
                           comments=comments, pagination=pagination)


@main.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author and \
            not current_user.can(Permission.ADMINISTER):
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.body = form.body.data
        db.session.add(post)
        flash('The post has been updated.')
        return redirect(url_for('.post', id=post.id))
    form.body.data = post.body
    return render_template('edit_post.html', form=form)


@main.route('/follow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    if current_user.is_following(user):
        flash('You are already following this user.')
        return redirect(url_for('.user', username=username))
    current_user.follow(user)
    flash('You are now following %s.' % username)
    return redirect(url_for('.user', username=username))


@main.route('/unfollow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    if not current_user.is_following(user):
        flash('You are not following this user.')
        return redirect(url_for('.user', username=username))
    current_user.unfollow(user)
    flash('You are not following %s anymore.' % username)
    return redirect(url_for('.user', username=username))


@main.route('/followers/<username>')
def followers(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followers.paginate(
        page, per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],
        error_out=False)
    follows = [{'user': item.follower, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('followers.html', user=user, title="Followers of",
                           endpoint='.followers', pagination=pagination,
                           follows=follows)


@main.route('/followed-by/<username>')
def followed_by(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followed.paginate(
        page, per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],
        error_out=False)
    follows = [{'user': item.followed, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('followers.html', user=user, title="Followed by",
                           endpoint='.followed_by', pagination=pagination,
                           follows=follows)


@main.route('/all')
@login_required
def show_all():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed', '', max_age=30*24*60*60)
    return resp


@main.route('/followed')
@login_required
def show_followed():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed', '1', max_age=30*24*60*60)
    return resp


@main.route('/moderate')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate():
    page = request.args.get('page', 1, type=int)
    pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'],
        error_out=False)
    comments = pagination.items
    return render_template('moderate.html', comments=comments,
                           pagination=pagination, page=page)


@main.route('/moderate/enable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_enable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = False
    db.session.add(comment)
    return redirect(url_for('.moderate',
                            page=request.args.get('page', 1, type=int)))


@main.route('/moderate/disable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_disable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = True
    db.session.add(comment)
    return redirect(url_for('.moderate',
                            page=request.args.get('page', 1, type=int)))

# ---------------------------------sq------------------------------------------

@main.route('/create', methods=['GET', 'POST'])
@login_required
def create_project():
    form = ProjectForm()
    
    # if current_user.can(Permission.WRITE_ARTICLES) and \
    #         form.validate_on_submit():

    if form.validate_on_submit():
        project = Project(name=form.name.data,
                           description=form.description.data,
                           subject=form.subject.data,
                           # this should be a list
                           students=[current_user._get_current_object()])
        db.session.add(project)
        db.session.commit()
        flash('successfully created')
        # return redirect(url_for('.project'))
        return redirect(url_for('.view_project', id=project.id))
    return render_template('create_project.html', form=form)

@main.route('/project/<int:id>', methods=['GET', 'POST'])
def view_project(id):
    project = Project.query.get_or_404(id)
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(body=form.body.data,
                          project=project,
                          author=current_user._get_current_object())
        db.session.add(comment)
        db.session.commit()
        flash('Your comment has been published.')
        return redirect(url_for('.view_project', id=project.id, page=-1))
    page = request.args.get('page', 1, type=int)
    if page == -1:
        page = (project.comments.count() - 1) / \
            current_app.config['FLASKY_COMMENTS_PER_PAGE'] + 1
    pagination = project.comments.order_by(Comment.timestamp.asc()).paginate(
        page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'],
        error_out=False)
    comments = pagination.items
    # deleted  posts=[post] from below
    return render_template('project.html', form=form,
                           projects=[project], comments=comments)

@main.route('/projects/<username>', methods=['GET', 'POST'])
def view_projects_by_user(username):
    """ getting 'instrumented list has no attribute order_by'
    because user.student_projects is a list and not a query object.
    so i'm changing user.student_projects.order_by(Project.timestamp.desc())
    to just user.student_projects """
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    pagination = user.student_projects.order_by(Project.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    projects = pagination.items
    return render_template('projects_by_user.html', user=user, projects=projects,
                           pagination=pagination)

@main.route('/edit-project/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_project(id):
    project = Project.query.get_or_404(id)
    if current_user not in project.students and \
            not current_user.can(Permission.ADMINISTER):
        abort(403)
    form = ProjectForm()
    if form.validate_on_submit():
        project.name = form.name.data
        project.subject = form.subject.data
        project.description = form.description.data
        db.session.add(project)
        # added this
        db.session.commit()
        flash('The post has been updated.')
        return redirect(url_for('.view_project', id=project.id))
    # fills in the form from previously entered data to be renedered in 
    # 'render_template'
    form.name.data = project.name
    form.subject.data = project.subject
    form.description.data = project.description
    return render_template('edit_post.html', form=form)

# @main.route('/all-mentors')
# def all_mentors():
#     pass

@main.route('/user/<username>/your-mentors')
def your_mentors(username):
    user = User.query.filter_by(username=username).first_or_404()
    mentors = User.query.all()
    return render_template('your/your_mentors.html', mentors=mentors)

@main.route('/user/<username>/your-students')
def your_students(username):
    user = User.query.filter_by(username=username).first_or_404()
    students = User.query.all()
    return render_template('your/your_mentors.html', people=students)

@main.route('/user/<username>/your-mentees')
def your_mentees(username):
    user = User.query.filter_by(username=username).first_or_404()
    mentees = User.query.all()
    return render_template('your/your_mentors.html', people=mentees)

@main.route('/user/<username>/your-kids')
def your_kids(username):
    user = User.query.filter_by(username=username).first_or_404()
    kids = User.query.all()
    return render_template('your/your_mentors.html', people=kids)

@main.route('/projects/search', methods=['GET', 'POST'])
def search_projects():
    projects = Project.query.all()
    blurb = {'body': "These are all of the projects"}
    return render_template('search.html', projects=projects, blurb=blurb)

@main.route('/search-mentors', methods=['GET', 'POST'])
def search_mentors():
    mentors = User.query.all()
    blurb = {'body': "These are all of the mentors"}
    return render_template('search_mentors.html', mentors=mentors, blurb=blurb)

@main.route('/search-mentors/<subject>', methods=['GET', 'POST'])
def search_mentors_by_subject(subject):
    """ still need to filter by mentor interests """
    mentors = User.query.filter_by(new_role='mentor').all()
                         # filter_by(subject.in_.User.interests).\
                         
    blurb = {'body': "These are all of the projects"}
    return render_template('search_mentors.html', mentors=mentors, 
                           blurb=blurb)

@main.route('/projects/search-by-subject/<subject>', methods=['GET', 'POST'])
def search_projects_by_subject(subject):
    possibilities = ["mathematics", "science", "engineering", "literature", 
                     "creative-writing", "music", "public service", 
                     "entrepreneurship", "art"]
    string_subject = str(subject)
    blurb = " Generous sponsors coming soon!"
    if string_subject in possibilities:
        projects = Project.query.filter_by(subject=string_subject).all()
    else:
        return redirect(url_for('.search_projects'))
    return render_template('search_by_subject.html', projects=projects, blurb=blurb)

@main.route('/projects/search-by-school/<school>', methods=['GET', 'POST'])
def search_projects_by_school(school):
    possibilities = ["ventures", "new-country", "big-ideas", "high-tech-high", 
                     "arcadia"]
    blurb_dict= {
        "ventures": "<a href='http://ventureacademies.org' target='_blank'>Ventures Academy \
            </a> is a new 7-12 Charter School in Minneapolis which utilizes \
            entrepreneurship and technology to inspire and engage its students.",

        "new-country": "<a href='http://www.newcountryschool.com/' target='_blank'> \
            Minnesota New Country School</a> is a \
            new 7-12 school in Henderson, Minnesota which allows their students \
            to take control of their learning through a completely project-\
            based curruculum.", 

         "big-ideas": "<a href='http://shawncornally.com/BIG/index.php' target='_blank'> \
            The Big Ideas Group</a> is a \"graduate school experience for \
            high school students -- located in Iowa City, Iowa.",

         "high-tech-high": "<a href='http://www.hightechhigh.org/' target='_blank'> \
            High Tech High</a> in San Diego is the premier project-based \
            high school in the world.",

         "arcadia": "<a href='https://artech.k12.mn.us/' target='_blank'> \
            Arcadia</a> is an awesome project-based school located in \
            Minnesota"}

    string_school = str(school)
    if string_school in possibilities:
        projects = Project.query.filter_by(subject=string_school).all()
        blurb=blurb_dict[string_school]
    else:
        return redirect(url_for('.search_projects'))
    return render_template('search_by_school.html', projects=projects, blurb=blurb)

@main.route('/project/<int:id>/versions/<int:version>', methods=['GET', 'POST'])
def view_project_version(id,version):
    pass

@main.route('/', methods=['GET','POST'])
def home():
    recent_projects = Project.query.order_by(Project.timestamp.desc()).limit(20).all()
    bunches = [recent_projects[0:4],recent_projects[4:8],recent_projects[8:12],
               recent_projects[12:16],recent_projects[16:20]]
    return render_template('home.html', bunches=bunches)

@main.route('/project/<int:id>/collaborate')
def collaborate(id):
    return render_template('collaborate.html', id=id)
    
@main.route('/project/<int:id>/volunteer')
def volunteer(id):
    return render_template('volunteer.html', id=id)    

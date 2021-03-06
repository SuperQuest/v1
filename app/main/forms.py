from flask.ext.wtf import Form
from wtforms import StringField, TextAreaField, BooleanField, SelectField,\
    SubmitField, SelectMultipleField
from wtforms.validators import Required, Length, Email, Regexp
from wtforms import ValidationError, widgets
from flask.ext.pagedown.fields import PageDownField
from ..models import Role, User


class NameForm(Form):
    name = StringField('What is your name?', validators=[Required()])
    submit = SubmitField('Submit')


class EditProfileForm(Form):
    name = StringField('Real name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')


class EditProfileAdminForm(Form):
    email = StringField('Email', validators=[Required(), Length(1, 64),
                                             Email()])
    username = StringField('Username', validators=[
        Required(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                          'Usernames must have only letters, '
                                          'numbers, dots or underscores')])
    confirmed = BooleanField('Confirmed')
    role = SelectField('Role', coerce=int)
    name = StringField('Real name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name)
                             for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, field):
        if field.data != self.user.email and \
                User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        if field.data != self.user.username and \
                User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')


class PostForm(Form):
    body = PageDownField("What's on your mind?", validators=[Required()])
    submit = SubmitField('Submit')


class CommentForm(Form):
    body = StringField('Enter your comment', validators=[Required()])
    submit = SubmitField('Submit')

# ---------------------------------sq------------------------------------------

subjects =[('mathematics', 'Mathematics'), ('science', 'Science'), 
        ('engineering', 'Engineering'), ('literature', 'Literature'),
        ('music', 'Music'), ('service', 'Service'), 
        ('entrepreneurship', 'Entrepreneurship'), ('art', 'Art'),
        ('public-service', 'Public Service'), 
        ('creative-writing', 'Creative Writing')]

class ProjectForm(Form):
    name = StringField('Give your project a name', validators=[Required()])
    description = StringField('Describe your project', validators=[Required()])
    subject = SelectField(u'What subject is your project in?', 
        choices=subjects)
    submit = SubmitField('Submit')


class SearchForm(Form):
    example = SelectMultipleField('Label', 
                      choices=subjects,
                      option_widget=widgets.CheckboxInput(),
                      widget=widgets.ListWidget(prefix_label=False))
    submit = SubmitField('Submit')

class ContactForm(Form):
    name = StringField('Name', validators=[Length(0, 64)])
    email = StringField('Email', validators=[Required(), Length(1, 64),
                                             Email()])
    message = TextAreaField('Message')
    submit = SubmitField('Submit')

class AdviseForm(Form):
    interest = TextAreaField("What interests you about this project?")
    help_offered = TextAreaField("How can you help?")
    submit = SubmitField('Submit')

class CollaborateForm(Form):
    interest = TextAreaField("What interests you about this project?")
    help_offered = TextAreaField("How can you help?")
    progress = TextAreaField("Have you made any progress towards a similar idea?")
    submit = SubmitField('Submit')
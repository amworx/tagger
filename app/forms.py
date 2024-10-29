from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, RadioField, HiddenField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Optional
from app.models import User, UserRole
from flask_wtf.file import FileField, FileAllowed

class AssetTypeForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=100)])
    code = StringField('Code', validators=[DataRequired(), Length(min=3, max=3)])
    submit = SubmitField('Submit')

class BuildingForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=100)])
    code = StringField('Code', validators=[DataRequired(), Length(min=3, max=3)])
    submit = SubmitField('Submit')

class DepartmentForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=100)])
    code = StringField('Code', validators=[DataRequired(), Length(min=3, max=3)])
    submit = SubmitField('Submit')

class LoginForm(FlaskForm):
    login = StringField('Username or Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')

class SettingsForm(FlaskForm):
    app_name = StringField('App Name', validators=[DataRequired()])
    interface_theme = RadioField('Interface Theme', choices=[('theme-light', 'Light'), ('theme-dark', 'Dark')])
    app_font = SelectField('Application Font', choices=[('Inter', 'Inter'), ('Noto Sans', 'Noto Sans')])
    submit = SubmitField('Save Changes')

class UserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match')])
    role = SelectField('Role', choices=[('user', 'User'), ('admin', 'Admin')])
    submit = SubmitField('Add User')

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        if 'obj' in kwargs:
            self.original_username = kwargs['obj'].username
            self.original_email = kwargs['obj'].email
        else:
            self.original_username = None
            self.original_email = None

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        if email.data != self.original_email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')

class SuperadminEditForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('New Password', validators=[Optional(), Length(min=6)])
    confirm_password = PasswordField('Confirm New Password', validators=[EqualTo('password', message='Passwords must match')])
    submit = SubmitField('Update')

    def __init__(self, original_email, *args, **kwargs):
        super(SuperadminEditForm, self).__init__(*args, **kwargs)
        self.original_email = original_email

    def validate_email(self, email):
        if email.data != self.original_email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is already in use. Please choose a different one.')

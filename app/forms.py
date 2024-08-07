import logging
from flask_wtf import FlaskForm
from wtforms import (
    StringField, SubmitField, IntegerField, FloatField, SelectField, 
    PasswordField, DateTimeField, BooleanField, SelectMultipleField, TextAreaField, 
    HiddenField, FieldList, FormField, FileField
)
from wtforms.validators import DataRequired, InputRequired, Email, EqualTo, URL, Optional, Length
from flask_wtf.file import FileAllowed
from wtforms.widgets import ListWidget, CheckboxInput
from .models import Worker, Role
from app import db
from .utils import get_account_managers, get_locations

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class RoleForm(FlaskForm):
    name = StringField('Role Name', validators=[DataRequired(), Length(max=64)])
    description = TextAreaField('Description', validators=[Length(max=256)])
    submit_add = SubmitField('Add Role')
    submit_delete = SubmitField('Delete Role')


class CSRFForm(FlaskForm):
    submit = SubmitField('Delete')


class RoleCheckboxForm(FlaskForm):
    pass

class RoleCapabilityField(FlaskForm):
    capability = BooleanField()
    
from wtforms.widgets import ListWidget, CheckboxInput

class EditWorkerForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone_number = StringField('Phone Number')
    is_admin = BooleanField('Is Admin')
    is_account_manager = BooleanField('Is Account Manager')
    role_capabilities = SelectMultipleField('Role Capabilities', choices=[], option_widget=CheckboxInput(), widget=ListWidget(prefix_label=False))
    submit = SubmitField('Update Worker')

    def __init__(self, *args, **kwargs):
        super(EditWorkerForm, self).__init__(*args, **kwargs)
        self.populate_roles()

    def populate_roles(self):
        roles = Role.query.all()
        self.role_capabilities.choices = [(str(role.id), role.name) for role in roles]
        
class AdminCreateWorkerForm(EditWorkerForm):
    temp_password = PasswordField('Temporary Password', validators=[DataRequired()])
    confirm_temp_password = PasswordField('Confirm Temporary Password', validators=[DataRequired(), EqualTo('temp_password')])
    submit = SubmitField('Create Worker')


class DynamicChoicesForm(FlaskForm):
    def update_choices(self, field_name, choices):
        getattr(self, field_name).choices = choices

class CrewRequestForm(FlaskForm):
    crew_id = HiddenField('Crew ID')
    start_time = DateTimeField('Start Date & Time', format='%Y-%m-%d %H:%M', validators=[DataRequired()])
    end_time = DateTimeField('End Date & Time', format='%Y-%m-%d %H:%M', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    roles_json = HiddenField('Roles JSON', validators=[DataRequired()])
    shift_type = SelectMultipleField('Shift Type', choices=[('Setup', 'Setup'), ('Show', 'Show'), ('Strike', 'Strike')], option_widget=CheckboxInput(), widget=ListWidget(prefix_label=False))
    submit = SubmitField('Add Crew Request')

class EventForm(DynamicChoicesForm):
    show_name = StringField('Show Name:', validators=[InputRequired(), DataRequired()])
    show_number = IntegerField('Show Number:', validators=[InputRequired(), DataRequired()])
    account_manager = SelectField('Account Manager:', choices=[], validators=[InputRequired(), DataRequired()])
    location = SelectField('Location:', choices=[], validators=[InputRequired(), DataRequired()])
    active = BooleanField('Active', default=True)
    submit = SubmitField('Submit')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.update_choices('account_manager', [(am.id, f'{am.first_name} {am.last_name}') for am in get_account_managers()])
        self.update_choices('location', [(loc.id, loc.name) for loc in get_locations()])

class LocationForm(FlaskForm):
    name = StringField('Location Name', validators=[DataRequired()])
    address = TextAreaField('Address', validators=[DataRequired()])
    loading_notes = TextAreaField('Loading Notes')
    dress_code = TextAreaField('Dress Code')
    other_info = TextAreaField('Other Information')
    submit = SubmitField('Save')

class PasswordFormBase(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])

class ChangePasswordForm(PasswordFormBase):
    submit = SubmitField('Change Password')

class UpdatePasswordForm(PasswordFormBase):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Update Password')

class UpdateProfileForm(DynamicChoicesForm):
    worker_select = SelectField('Select Worker', choices=[], coerce=int)
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone_number = StringField('Phone Number')
    is_admin = BooleanField('Admin')
    is_account_manager = BooleanField('Account Manager')
    submit = SubmitField('Update')

    def __init__(self, view_as_employee=False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if view_as_employee:
            del self.is_admin
            del self.is_account_manager
            del self.worker_select
        else:
            self.update_choices('worker_select', [(worker.id, f'{worker.first_name} {worker.last_name}') for worker in Worker.query.all()])

class ShiftForm(DynamicChoicesForm):
    start = StringField('Shift Start:', id='shift_start', validators=[InputRequired(), DataRequired()])
    end = StringField('Shift End:', id='shift_end', validators=[InputRequired(), DataRequired()])
    show_number = IntegerField('Show Number:', validators=[InputRequired(), DataRequired()])
    worker = SelectField('Worker:', coerce=int, validators=[InputRequired(), DataRequired()])
    roles = SelectMultipleField('Roles:', choices=[], validators=[InputRequired(), DataRequired()])
    location = SelectField('Location:', choices=[], validators=[InputRequired(), DataRequired()])
    submit = SubmitField('Submit')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.update_choices('location', [(loc.id, loc.name) for loc in get_locations()])
        self.update_choices('roles', [(role.id, role.name) for role in Role.query.all()])

class ExpenseForm(DynamicChoicesForm):
    receipt_number = IntegerField('Receipt Number:', validators=[InputRequired(), DataRequired()])
    date = StringField('Date:', id='expdatepick', validators=[InputRequired(), DataRequired()])
    show_number = IntegerField('Event Number:', validators=[InputRequired(), DataRequired()])
    details = StringField('Expense Details:', validators=[InputRequired(), DataRequired()])
    net = FloatField('Subtotal:', validators=[InputRequired(), DataRequired()])
    hst = FloatField('HST:', validators=[InputRequired(), DataRequired()])
    receipt = FileField('Receipt', validators=[FileAllowed(['jpg', 'jpeg', 'png', 'pdf'], 'Images and PDFs only!')])
    worker = SelectField('Worker:', coerce=int, validators=[InputRequired(), DataRequired()])
    submit = SubmitField('Submit')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.update_choices('worker', [(worker.id, f'{worker.first_name} {worker.last_name}') for worker in Worker.query.all()])

class NoteForm(FlaskForm):
    notes = TextAreaField('Note Content', validators=[DataRequired()])
    account_manager_only = BooleanField('Visible to Account Managers Only')
    account_manager_and_td_only = BooleanField('Visible to Account Managers and TDs Only')
    submit_note = SubmitField('Add Note')

class DocumentForm(FlaskForm):
    document = FileField('Upload Document', validators=[FileAllowed(['pdf', 'jpeg', 'jpg', 'png', 'docx', 'xlsx'], 'Documents only!')])
    submit = SubmitField('Upload Document')

class SharePointForm(FlaskForm):
    sharepoint_link = StringField('SharePoint Link', validators=[DataRequired(), URL()])
    submit = SubmitField('Update Link')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), DataRequired(), Email()])
    password = PasswordField('Password', validators=[InputRequired(), DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone_number = StringField('Phone Number', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

class RequestResetForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

class ResetPasswordForm(PasswordFormBase):
    submit = SubmitField('Reset Password')

class AssignWorkerForm(FlaskForm):
    worker = SelectField('Select Worker', coerce=int, validators=[DataRequired()])
    role = HiddenField('Role', validators=[DataRequired()])
    crew_id = HiddenField('Crew ID', validators=[DataRequired()])
    submit = SubmitField('Assign Worker')

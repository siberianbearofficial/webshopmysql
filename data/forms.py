from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, SelectField
from wtforms.validators import DataRequired


class YesNoForm(FlaskForm):
    cancel = SubmitField("Отмена")
    yes = SubmitField("Подтвердить")


class StartForm(FlaskForm):
    submit = SubmitField("Готово")


class LoginForm(StartForm):
    email = StringField("Email")
    password = PasswordField("Password")


class RegisterForm(LoginForm):
    name = StringField("Name")


class AdminForm(RegisterForm):
    access = SelectField('Access', choices=[(1, 'Admin'), (2, 'Owner')])

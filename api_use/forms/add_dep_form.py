from flask_wtf import FlaskForm
from wtforms import EmailField, SubmitField, IntegerField, StringField
from wtforms.validators import DataRequired


class AddDepForm(FlaskForm):
    title = StringField('Department Title', validators=[DataRequired()])
    chief = IntegerField('Chief id', validators=[DataRequired()])
    members = StringField('Members', validators=[DataRequired()])
    email = EmailField('Почта', validators=[DataRequired()])
    submit = SubmitField('Submit')
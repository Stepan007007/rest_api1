from flask_wtf import FlaskForm
from wtforms import BooleanField, SubmitField, IntegerField, StringField
from wtforms.validators import DataRequired


class AddJobForm(FlaskForm):
    job = StringField('Job Title', validators=[DataRequired()])
    team_leader = IntegerField('Team Leader id', validators=[DataRequired()])
    work_size = IntegerField('Work Size', validators=[DataRequired()])
    collaborators = StringField('Collaborators', validators=[DataRequired()])
    is_finished = BooleanField('Is job finished?')
    submit = SubmitField('Submit')
from flask import Flask, jsonify, render_template, redirect, make_response

from flask_wtf import FlaskForm

from wtforms import PasswordField, StringField, IntegerField, SubmitField, DateTimeField, BooleanField, FieldList
from wtforms.validators import DataRequired, Length, Optional
from werkzeug.security import generate_password_hash

from data.db_session import global_init, create_session

from flask_login import LoginManager, login_required, login_user, current_user, logout_user

from data.marsone import User, Jobs, Department

from werkzeug.security import check_password_hash

import datetime

from data import json_api, user_api


def create_user_from_form(form):
    # Получаем словарь из формы
    form_data = form.data.copy()

    # Удаляем лишние поля
    form_data.pop('csrf_token', None)
    form_data.pop('submit', None)

    # Обрабатываем пароль
    if 'password' in form_data:
        form_data['hashed_password'] = generate_password_hash(
            form_data.pop('password'))

    # Возвращаем готовый объект пользователя
    return User(**form_data)


global_init('db/info.db')

app = Flask(__name__)
app.config['SECRET_KEY'] = 'beta_gama_beta'
login_manager = LoginManager()
login_manager.init_app(app)


class RegisterForm(FlaskForm):
    surname = StringField('Фамилия', validators=[Optional(), Length(max=50)])
    name = StringField('Имя', validators=[Optional(), Length(max=50)])
    age = IntegerField('Возраст', validators=[Optional()])
    position = StringField('Должность', validators=[
        Optional(), Length(max=100)])
    speciality = StringField('Специальность', validators=[
        Optional(), Length(max=100)])
    address = StringField('Адрес', validators=[Optional(), Length(max=200)])
    email = StringField('Email', validators=[
        DataRequired(), Length(max=120)])
    password = PasswordField('Пароль', validators=[
        DataRequired(), Length(min=6)])
    submit = SubmitField('Зарегистрироваться/Войти')


@login_manager.user_loader
def load_user(user_id):
    session = create_session()
    return session.query(User).get(user_id)


@app.route('/login', methods=['POST', 'GET'])
def login():
    form = RegisterForm()
    if form.validate_on_submit():
        db_sess = create_session()
        user = db_sess.query(User).filter(
            User.email == form.email.data).first()
        if user and check_password_hash(user.hashed_password, form.password.data):
            login_user(user, remember=True)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/')
def home():
    ses = create_session()
    if current_user.is_authenticated:
        jobs = ses.query(Jobs).all()
        return render_template('home.html', jobs=jobs, current_user=current_user)
    else:
        return redirect('/login')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')


@app.route('/register', methods=['POST', 'GET'])
def register():
    form = RegisterForm()
    ses = create_session()
    if form.validate_on_submit():
        try:
            has_data = ses.query(User).filter(
                User.email == form.email.data).all()
            if has_data:
                print(has_data)
                return render_template('registet.html',
                                       message='такие данные уже есть', form=form)
            else:
                user = create_user_from_form(form)
                ses.add(user)
                ses.commit()
                return redirect('/login')
        except Exception as e:
            print(e)
            return redirect('/register')
    return render_template('register.html', form=form)


class JobForm(FlaskForm):
    job = StringField('Job Description', validators=[DataRequired()])
    work_size = IntegerField('Work Size', validators=[DataRequired()])
    collaborators = FieldList(StringField('Collaborator'), min_entries=1)
    start_date = DateTimeField(
        'Start Date', default=datetime.datetime.now, validators=[DataRequired()])
    end_date = DateTimeField(
        'End Date', default=datetime.datetime.now(), validators=[Optional()])
    is_finished = BooleanField('Is Finished', default=False)
    submit = SubmitField('Отправить')


@app.route('/addjob', methods=['POST', 'GET'])
def addjob():
    form = JobForm()
    if form.validate_on_submit():
        try:
            ses = create_session()
            new_job = Jobs(
                team_leader=current_user.id,
                job=form.job.data,
                work_size=form.work_size.data,
                collaborators=form.collaborators.data,
                start_date=form.start_date.data,
                end_date=form.end_date.data,
                is_finished=form.is_finished.data
            )

            ses.add(new_job)
            ses.commit()
            return redirect('/')
        except Exception as e:
            print(e)
            return redirect('/addjob')
    return render_template('addjobs.html', form=form)


@app.route('/ed/<int:id_>', methods=['POST', 'GET'])
def editjob(id_):
    ses = create_session()
    get_ = ses.query(Jobs).get(id_)
    if get_.team_leader != current_user.id and current_user.id != 1:
        return redirect('/')

    get_data = get_.__dict__.copy()
    sp = list(get_data.keys())
    for i in ['team_leader', 'id']:
        sp.remove(i)

    dicters = {k: get_data[k] for k in sp}
    form = JobForm(**dicters)
    if form.validate_on_submit():
        try:
            get_.job = form.job.data
            get_.work_size = form.work_size.data
            get_.collaborators = form.collaborators.data
            get_.end_date = form.end_date.data
            get_.start_date = form.start_date.data
            get_.is_finished = form.is_finished.data
            ses.commit()
            return redirect('/')
        except Exception as e:
            print(e)
    return render_template('addjobs.html', form=form)


@app.route('/del/<int:id_>', methods=['GET', 'POST'])
def delet(id_):
    ses = create_session()
    get_ = ses.query(Jobs).get(id_)
    if current_user.id == 1 or current_user.id == get_.team_leader:
        ses.delete(get_)
        ses.commit()
    return redirect('/')


# Работа с департаментом


class DeparamentForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    members = FieldList(IntegerField('Member ID'), min_entries=1)
    email = StringField('Email', validators=[DataRequired()])
    submit = SubmitField('Отправить')


@app.route('/adddep', methods=['POST', 'GET'])
def adddep():
    form = DeparamentForm()
    if form.validate_on_submit():
        try:
            ses = create_session()
            new_dep = Department(title=form.title.data,
                                 members=form.members.data,
                                 email=form.email.data,
                                 chief=current_user.id)

            ses.add(new_dep)
            ses.commit()
            return redirect('/departments')
        except Exception as e:
            print(e)
            return redirect('/adddep')
    return render_template('addjobs.html', form=form)


@app.route('/eddep/<int:id_>', methods=['POST', 'GET'])
def editdep(id_):
    ses = create_session()
    get_ = ses.query(Department).get(id_)
    if get_.chief != current_user.id and current_user.id != 1:
        return redirect('/departments')

    get_data = get_.__dict__.copy()
    sp = list(get_data.keys())
    for i in ['chief', 'id']:
        sp.remove(i)

    dicters = {k: get_data[k] for k in sp}
    form = DeparamentForm(**dicters)
    if form.validate_on_submit():
        try:
            get_.title = form.title.data
            get_.members = form.members.data
            get_.email = form.email.data
            ses.commit()
            return redirect('/departments')
        except Exception as e:
            print(e)
    return render_template('addjobs.html', form=form)


@app.route('/deldep/<int:id_>', methods=['GET', 'POST'])
def deletee(id_):
    ses = create_session()
    get_ = ses.query(Department).get(id_)
    if current_user.id == 1 or current_user.id == get_.chief:
        ses.delete(get_)
        ses.commit()
    return redirect('/departments')


@app.route('/departments')
def homedep():
    ses = create_session()
    if current_user.is_authenticated:
        jobs = ses.query(Department).all()
        return render_template('departmnt.html', jobs=jobs, current_user=current_user)
    else:
        return redirect('/login')


@app.errorhandler(400)
def bad_reuqest(error):
    return make_response(jsonify({'error': error}))


if __name__ == '__main__':
    app.register_blueprint(json_api.blueprint)
    app.register_blueprint(user_api.blueprint)
    app.run(port=8080, host='127.0.0.1')
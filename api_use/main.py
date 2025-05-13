from io import BytesIO
from os import abort
from urllib.parse import urlencode
import os
import requests
from flask import Flask, render_template, redirect, request, jsonify
from data import db_session, jobs_api, user_api
from data.departments import Department
from data.users import User
from data.jobs import Jobs
from forms.user import RegisterForm
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from forms.login_form import LoginForm
from forms.add_job_form import AddJobForm
from forms.add_dep_form import AddDepForm
import datetime

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)

def main():
    db_session.global_init("db/blogs.db")
    app.register_blueprint(jobs_api.blueprint)
    app.register_blueprint(user_api.blueprint)
    app.run()
    data = [['Scott', 'Murphy', 'Ghost', 'Back'], ["Ridley", 'Trevor', 'Nick', 'Taylor'], [21, 22, 34, 54],
            ['captain', 'assistant', 'assistant', 'assistant'], ['research engineer', 'exobiologist', 'cook', 'doctor'],
            ['module_1', 'module_1', 'module_2', 'module_1'],
            ["scott_chief@mars.org", "murphy@mars.org", "ghost@mars.org", "back@mars.org"],
            ['London', 'Madrid', 'New York', 'Manchester']]
    db_sess = db_session.create_session()
    for i in range(4):
        user = User()
        user.surname = data[0][i]
        user.name = data[1][i]
        user.age = data[2][i]
        user.position = data[3][i]
        user.speciality = data[4][i]
        user.address = data[5][i]
        user.email = data[6][i]
        user.city_from = data[7][i]
        db_sess.add(user)
        db_sess.commit()
        if user.id == 1:
            user.set_password('Iamcaptain')

    job = Jobs()
    job.team_leader = 1
    job.job = 'deployment of residential modules 1 and 2'
    job.work_size = 15
    job.collaborators = '2,3'
    job.start_date = datetime.datetime.today()
    job.is_finished = False
    db_sess.add(job)
    db_sess.commit()

    job1 = Jobs()
    job1.team_leader = 3
    job1.job = 'Exploration of mineral resources'
    job1.work_size = 24
    job1.collaborators = '1,2,4'
    job1.start_date = datetime.datetime.today()
    job1.is_finished = False
    db_sess.add(job1)
    db_sess.commit()

    dep = Department()
    dep.title = 'Геологическая разведка'
    dep.chief = '1'
    dep.members = '2,3'
    dep.email = 'geolog@mars.ru'
    db_sess.add(dep)
    db_sess.commit()

    dep1 = Department()
    dep1.title = 'Починка марсохода'
    dep1.chief = '4'
    dep1.members = '1,2,3'
    dep1.email = 'marsohod@mars.ru'
    db_sess.add(dep1)
    db_sess.commit()
    return

@app.route("/")
@app.route('/index')
def index():
    db_session.global_init('db/blogs.db')
    db_sess = db_session.create_session()
    jobs = db_sess.query(Jobs).all()
    return render_template("index.html", jobs=jobs)

@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            email=form.email.data,
            surname=form.surname.data,
            name=form.name.data,
            age=form.age.data,
            position=form.position.data,
            speciality=form.speciality.data,
            address=form.address.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")

@app.route('/add_job', methods=['GET', 'POST'])
@login_required
def add_job():
    form = AddJobForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        job = Jobs(
            job=form.job.data,
            team_leader=form.team_leader.data,
            work_size=form.work_size.data,
            collaborators=form.collaborators.data,
            is_finished=form.is_finished.data
        )
        current_user.jobs.append(job)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/')
    return render_template('add_job.html', title='Adding a job', form=form)

@app.route('/jobs/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_job(id):
    form = AddJobForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        jobs = db_sess.query(Jobs).filter(Jobs.id == id).first()
        if jobs:
            form.job.data = jobs.job
            form.team_leader.data = jobs.team_leader
            form.work_size.data = jobs.work_size
            form.collaborators.data = jobs.collaborators
            form.is_finished.data = jobs.is_finished
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        jobs = db_sess.query(Jobs).filter(Jobs.id == id).first()
        if jobs:
            jobs.job = form.job.data
            jobs.team_leader = form.team_leader.data
            jobs.work_size = form.work_size.data
            jobs.collaborators = form.collaborators.data
            jobs.is_finished = form.is_finished.data
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('add_job.html', title='Adding a job', form=form)

@app.route('/jobs_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def jobs_delete(id):
    db_sess = db_session.create_session()
    jobs = db_sess.query(Jobs).filter(Jobs.id == id).first()
    if jobs:
        db_sess.delete(jobs)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')

@app.route("/department")
def department():
    db_session.global_init('db/blogs.db')
    db_sess = db_session.create_session()
    departments = db_sess.query(Department).all()
    return render_template("departments.html", departments=departments)

@app.route('/add_department', methods=['GET', 'POST'])
@login_required
def add_department():
    form = AddDepForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        dep = Department(
            title=form.title.data,
            chief=form.chief.data,
            members=form.members.data,
            email=form.email.data
        )
        db_sess.add(dep)
        db_sess.commit()
        return redirect('/department')
    return render_template('add_dep.html', title='Adding a Department', form=form)

@app.route('/department/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_dep(id):
    form = AddDepForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        deps = db_sess.query(Department).filter(Department.id == id).first()
        if deps:
            form.title.data = deps.title
            form.chief.data = deps.chief
            form.members.data = deps.members
            form.email.data = deps.email
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        deps = db_sess.query(Department).filter(Department.id == id).first()
        if deps:
            deps.title = form.title.data
            deps.chief = form.chief.data
            deps.members = form.members.data
            deps.email = form.email.data
            db_sess.commit()
            return redirect('/department')
        else:
            abort(404)
    return render_template('add_dep.html', title='Adding a Department', form=form)

@app.route('/department_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def department_delete(id):
    db_sess = db_session.create_session()
    dep = db_sess.query(Department).filter(Department.id == id).first()
    if dep:
        db_sess.delete(dep)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/department')


class image():
    def __init__(self, address):
        self.address = address
        self.api_key = "8013b162-6b42-4997-9691-77b7074026e0"

    def get_image(self):
        try:
            response = requests.get(
                f"https://geocode-maps.yandex.ru/1.x/",
                params={"format": "json", "geocode": self.address, "apikey": self.api_key}
            )
            if response.status_code != 200:
                raise requests.HTTPError(response.text)
            res = response.json()
            pos = res["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]["Point"]["pos"]
            lon, lat = pos.split()
            map_params = {
                "ll": f"{lon},{lat}",
                "z": "10",
                "l": "map",
                "size": "650,450",
                "apikey": "f3a0fe3a-b07e-4840-a1da-06f18b2ddf13"
            }
            image = requests.get(
                f"https://static-maps.yandex.ru/1.x/?{requests.compat.urlencode(map_params)}"
            )
            if image.status_code == 200:
                return image.content
        except requests.RequestException as e:
            print(f"Ошибка при получении изображения: {e}")
            return None


@app.route('/users_show/<int:user_id>')
def users_show(user_id):
    path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static/img/image{}.png'.format(user_id))
    response = requests.get(f'http://127.0.0.1:5000/api/users/{user_id}')
    if response.status_code != 200:
        try:
            error_message = response.json().get('error')
        except ValueError:
            pass
        return jsonify({"error": error_message}), response.status_code
    else:
        try:
            user_data = response.json()['user'][0]
        except (KeyError, IndexError):
            pass
    city_from = user_data.get('city_from')
    if city_from is not None:
        try:
            geocoder = image(city_from)
            img = geocoder.get_image()
            if img:
                with open(path, 'wb') as file:
                    file.write(img)
        except requests.exceptions.RequestException:
            pass
    return render_template('user.html', user=user_data, img=f"/static/img/image{user_id}.png")

if __name__ == '__main__':
    main()
from flask import jsonify, make_response, request
from . import db_session
from .marsone import User
import flask
from datetime import datetime
from werkzeug.security import generate_password_hash

blueprint = flask.Blueprint('user_api', __name__, template_folder='templates')


@blueprint.route('/api/users', methods=['GET'])
def get_user():
    ses = db_session.create_session()
    users = ses.query(User).all()
    sp = (
    'id', 'surname', 'name', 'age', 'position', 'speciality', 'address', 'email', 'hashed_password', 'modified_date')
    if not users:
        return make_response(jsonify({'error': 'not_found'}), 404)
    return jsonify(
        {
            'user': [user.to_dict(only=sp) for user in users]

        }
    )


@blueprint.route('/api/users/<int:user_id>')
def get_only_one_users(user_id):
    ses = db_session.create_session()
    user = ses.query(User).get(user_id)
    sp = ('surname', 'name', 'age', 'position', 'speciality', 'address', 'email', 'hashed_password', 'modified_date')
    if not user:
        return make_response(jsonify({'error': 'not_found'}), 404)
    return jsonify(
        {
            'user': user.to_dict(sp)
        }
    )


@blueprint.route('/api/users', methods=['POST'])
def create_user():
    sp = ('surname', 'name', 'age', 'position', 'speciality', 'address', 'email', 'hashed_password', 'modified_date')
    if not request.json:
        return make_response(jsonify({'error': 'need data'}), 400)

    elif not all(key in request.json for key in sp):
        return make_response(jsonify({'errors': 'neeed_moredata'}), 400)

    try:

        ses = db_session.create_session()
        new_user = User(
            surname=request.json.get('surname'),  # .get() вместо [], чтобы не было KeyError, если поля нет
            name=request.json.get('name'),
            age=request.json['age'],
            position=request.json['position'],
            speciality=request.json['speciality'],
            address=request.json.get('address'),
            email=request.json.get('email'),
            hashed_password=generate_password_hash(request.json.get('hashed_password')),
            modified_date=datetime.fromisoformat(
                request.json['modified_date']) if 'modified_date' in request.json else None
        )
        ses.add(new_user)
        ses.commit()
        return jsonify({'id': new_user.id})
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 500)


@blueprint.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    ses = db_session.create_session()
    try:
        user = ses.query(User).get(user_id)
        if not user:
            return make_response(jsonify({'error': 'pls send corret id'}), 400)
        ses.delete(user)
        ses.commit()
        return jsonify({'success': 'ok'})
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 400)


@blueprint.route('/api/users/<int:user_id>', methods=['PUT'])
def put_jobs(user_id):
    try:
        if not request.json:
            return make_response(jsonify({'error': 'need data'}), 400)
        ses = db_session.create_session()

        sp = (
        'surname', 'name', 'age', 'position', 'speciality', 'address', 'email', 'hashed_password', 'modified_date')
        user = ses.query(User).get(user_id)
        if user is None:
            return make_response(jsonify({'error': 'pls send corret id'}), 400)
        elif not all(key in request.json for key in sp):
            return make_response(jsonify({'errors': 'neeed_moredata'}), 400)

        user.surname = request.json['surname']
        user.name = request.json['name']
        user.age = request.json['age']
        user.position = request.json['position']
        user.speciality = request.json['speciality']
        user.address = request.json['address']
        user.email = request.json['email']
        user.hashed_password = generate_password_hash(request.json['hashed_password'])
        user.modified_date = datetime.fromisoformat(request.json['modified_date'])  # Конвертация строки в datetime
        ses.commit()

        return jsonify({"sec": f'{user.id}'})

    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 500)

import flask
from flask import jsonify, make_response, request

from data import db_session
from data.users import User

blueprint = flask.Blueprint(
    'users_api',
    __name__,
    template_folder='templates'
)


@blueprint.route('/api/users', methods=['GET', 'POST'])
def users():
    if request.method == 'GET':
        db_sess = db_session.create_session()
        users = db_sess.query(User).all()
        return jsonify(
            {
                'users':
                    [item.to_dict(only=('surname', 'name', 'age', 'position', 'speciality', 'address', 'email'))
                     for item in users]
            }
        )
    if not request.json:
        return make_response(jsonify({'error': 'Empty request'}), 400)
    elif not all(key in request.json for key in
                 ['surname', 'name', 'age', 'position', 'speciality', 'address', 'email']):
        return make_response(jsonify({'error': 'Bad request'}), 400)
    elif any(key not in ['surname', 'name', 'age', 'position', 'speciality', 'address', 'email'] for key in request.json):
        return make_response(jsonify({'error': 'Bad request'}), 400)
    db_sess = db_session.create_session()
    user = User(
        surname=request.json['surname'],
        name=request.json['name'],
        age=request.json['age'],
        position=request.json['position'],
        speciality=request.json['speciality'],
        address=request.json['address'],
        email=request.json['email']
    )
    db_sess.add(user)
    db_sess.commit()
    return jsonify({'id': user.id})

@blueprint.route('/api/users/<user_id>', methods=['GET'])
def users_id(user_id):
    db_sess = db_session.create_session()
    if not user_id.isdigit():
        return make_response(jsonify({'error': 'Неверный формат ID пользователя.'}), 400)

    user = db_sess.query(User).filter(User.id == int(user_id)).first()
    if not user:
        return make_response(jsonify({'error': 'Пользователь не найден.', 'status': 404}), 404)

    return jsonify({
        'user': [{
            'surname': user.surname,
            'name': user.name,
            'age': user.age,
            'position': user.position,
            'speciality': user.speciality,
            'address': user.address,
            'email': user.email,
            'city_from': user.city_from
        }]
    }), 200

@blueprint.route('/api/del_users/<int:users_id>', methods=['DELETE'])
def delete_users(users_id):
    db_sess = db_session.create_session()
    users = db_sess.query(User).get(users_id)
    if not users:
        return make_response(jsonify({'error': 'Not found'}), 404)
    db_sess.delete(users)
    db_sess.commit()
    return jsonify({'success': 'OK'})

@blueprint.route('/api/edit_user/<int:user_id>', methods=['PUT'])
def edit_user(user_id):
    if not request.json:
        return make_response(jsonify({'error': 'Empty request'}), 400)
    required_fields = ['surname', 'name', 'age', 'position', 'speciality', 'address', 'email']
    if not all(key in request.json for key in required_fields):
        return make_response(jsonify({'error': 'Bad request'}), 400)
    db_sess = db_session.create_session()
    user = db_sess.query(User).get(user_id)
    if not user:
        return make_response(jsonify({'error': 'Job not found'}), 404)
    user.surname = request.json.get('surname')
    user.name = request.json.get('name')
    user.age = request.json.get('age')
    user.position = request.json.get('position')
    user.speciality = request.json.get('speciality')
    user.address = request.json.get('address')
    user.email = request.json.get('email')
    db_sess.commit()
    return jsonify({'success': 'OK'})

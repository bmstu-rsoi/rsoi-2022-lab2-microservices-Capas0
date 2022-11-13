import requests
from flask import Blueprint, request, jsonify

api = Blueprint('api', __name__)

reservation_api = 'http://reservation:8070/api/v1'
library_api = 'http://library:8060/api/v1'
rating_api = 'http://rating:8050/api/v1'


@api.route('/libraries', methods=['GET'])
def list_libraries():
    response = requests.get(f'{library_api}/libraries', params=dict(request.args))
    return jsonify(response.json()), response.status_code


@api.route('/libraries/<library_uid>/books', methods=['GET'])
def get_library_books(library_uid):
    response = requests.get(f'{library_api}/libraries/{library_uid}/books', params=dict(request.args))
    return jsonify(response.json()), response.status_code


@api.route('/rating', methods=['GET'])
def get_rating():
    response = requests.get(f'{rating_api}/rating', headers=dict(request.headers))
    return jsonify(response.json()), response.status_code


def fill_reservation(reservation):
    book_uid = reservation.pop('bookUid')
    library_uid = reservation.pop('libraryUid')
    reservation['book'] = requests.get(f'{library_api}/books/{book_uid}').json()
    reservation['library'] = requests.get(f'{library_api}/libraries/{library_uid}').json()


@api.route('/reservations', methods=['GET'])
def list_reservations():
    reservations = requests.get(f'{reservation_api}/reservations', headers=dict(request.headers)).json()
    for reservation in reservations:
        fill_reservation(reservation)

    return jsonify(reservations)


@api.route('/reservations', methods=['POST'])
def take_book():
    with requests.Session() as session:
        session.headers.update(request.headers)

        rented = len(session.get(f'{reservation_api}/reservations').json())
        stars = session.get(f'{rating_api}/rating').json()['stars']
        if rented >= stars:
            return jsonify({
                'message': 'Maximum rented books number has reached',
                'errors': []
            })

        args = request.json
        library_uid = args['libraryUid']
        book_uid = args['bookUid']
        r = session.patch(f"{library_api}/libraries/{library_uid}/books/{book_uid}", json={'available_count': 0})
        if r.status_code != 200:
            return jsonify(r.json()), r.status_code

        r = session.post(f'{reservation_api}/reservations', json=request.json)
        if r.status_code != 201:
            return jsonify(r.json()), r.status_code

        reservation = r.json()
        fill_reservation(reservation)
        reservation['rating'] = {'stars': stars}

    return jsonify(reservation)

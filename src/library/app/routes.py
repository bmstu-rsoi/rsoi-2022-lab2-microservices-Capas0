from flask import Blueprint, jsonify, request
from marshmallow import ValidationError

from .base import db
from .models import Library, Book, LibraryBook
from .schemas import (
    LibraryPaginationRequestSchema,
    LibraryPaginationResponseSchema,
    LibraryBookPaginationRequestSchema,
    LibraryBookPaginationResponseSchema
)

api = Blueprint('api', __name__)


def format_errors(messages):
    for field, errors in messages.items():
        for error in errors:
            yield {'field': field, 'error': error}


@api.route('/libraries', methods=['GET'])
def list_libraries():
    try:
        args = LibraryPaginationRequestSchema().load(request.args)
    except ValidationError as err:
        return jsonify({
            'message': 'Invalid data',
            'errors': list(format_errors(err.messages))
        }), 400

    libraries = db.paginate(
        db.select(Library).where(Library.city == args['city']),
        page=args.get('page'),
        per_page=args.get('size'),
        count=True
    )

    return jsonify(LibraryPaginationResponseSchema().dump(libraries)), 200


@api.route('/libraries/<library_uid>/books', methods=['GET'])
def get_library_books(library_uid):
    try:
        args = LibraryBookPaginationRequestSchema().load(request.args)
    except ValidationError as err:
        return jsonify({
            'message': 'Invalid data',
            'errors': list(format_errors(err.messages))
        }), 400

    page = args.get('page', 1)
    per_page = args.get('size', 20)

    books_count = db.session.execute(
        db.select(db.func.count(Book.id))
        .join_from(Book, LibraryBook, Book.id == LibraryBook.book_id)
        .join(Library)
        .where(Library.library_uid == library_uid)
    ).scalars().one()
    books_items = db.session.execute(
        db.select(*Book.__table__.columns, LibraryBook.available_count)
        .join(LibraryBook)
        .join(Library)
        .where(Library.library_uid == library_uid)
        .limit(per_page).offset((page - 1) * per_page)
    ).all()

    return jsonify(LibraryBookPaginationResponseSchema().dump({
        "items": books_items,
        "page": page,
        "per_page": per_page,
        "total": books_count
    })), 200

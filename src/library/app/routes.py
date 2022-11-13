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

BOOKS_COUNT_TEMPLATE = (
    db.select(db.func.count(Book.id))
    .join_from(Book, LibraryBook, Book.id == LibraryBook.book_id)
    .join(Library)
)
BOOKS_ITEMS_TEMPLATE = (
    db.select(*Book.__table__.columns, LibraryBook.available_count)
    .join(LibraryBook)
    .join(Library)
)


def format_errors(messages):
    for field, errors in messages.items():
        for error in errors:
            yield {'field': field, 'error': error}


def format_validation_error(text, error):
    return {
        'message': text,
        'errors': list(format_errors(error.messages))
    }


@api.route('/libraries', methods=['GET'])
def list_libraries():
    try:
        args = LibraryPaginationRequestSchema().load(request.args)
    except ValidationError as err:
        return jsonify(format_validation_error('Invalid data', err)), 400

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
        return jsonify(format_validation_error('Invalid data', err)), 400

    page = args.get('page', 1)
    per_page = args.get('size', 20)
    show_all = args.get('show_all', False)

    books_count_stmt = BOOKS_COUNT_TEMPLATE.where(Library.library_uid == library_uid)
    books_items_stmt = BOOKS_ITEMS_TEMPLATE.where(Library.library_uid == library_uid)

    if not show_all:
        books_count_stmt = books_count_stmt.where(LibraryBook.available_count > 0)
        books_items_stmt = books_items_stmt.where(LibraryBook.available_count > 0)

    books_count = db.session.execute(books_count_stmt).scalars().one()
    books_items = db.session.execute(
        books_items_stmt.limit(per_page).offset((page - 1) * per_page)
    ).all()

    return jsonify(LibraryBookPaginationResponseSchema().dump({
        "items": books_items,
        "page": page,
        "per_page": per_page,
        "total": books_count
    })), 200

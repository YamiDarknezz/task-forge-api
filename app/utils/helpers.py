from flask import request, current_app, jsonify
from datetime import datetime
from dateutil import parser as date_parser


def success_response(data=None, message=None, status_code=200):
    """
    Generate a successful JSON response
    """
    response = {
        'success': True
    }

    if message:
        response['message'] = message

    if data is not None:
        response['data'] = data

    return jsonify(response), status_code


def error_response(message, error=None, status_code=400):
    """
    Generate an error JSON response
    """
    response = {
        'success': False,
        'message': message
    }

    if error:
        response['error'] = error

    return jsonify(response), status_code


def get_pagination_params():
    """
    Extract pagination parameters from request args
    Returns: (page, per_page, offset)
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page',
                                current_app.config.get('DEFAULT_PAGE_SIZE', 10),
                                type=int)

    max_per_page = current_app.config.get('MAX_PAGE_SIZE', 100)
    per_page = min(per_page, max_per_page)

    if page < 1:
        page = 1
    if per_page < 1:
        per_page = 10

    offset = (page - 1) * per_page

    return page, per_page, offset


def paginate(query, page=None, per_page=None):
    """
    Paginate a SQLAlchemy query
    Returns: (items, pagination_meta)
    """
    if page is None or per_page is None:
        page, per_page, _ = get_pagination_params()

    total = query.count()
    items = query.limit(per_page).offset((page - 1) * per_page).all()

    total_pages = (total + per_page - 1) // per_page

    pagination_meta = {
        'page': page,
        'per_page': per_page,
        'total': total,
        'total_pages': total_pages,
        'has_next': page < total_pages,
        'has_prev': page > 1
    }

    return items, pagination_meta


def parse_date(date_string):
    """
    Parse a date string to datetime object
    Supports various formats
    """
    if not date_string:
        return None

    try:
        return date_parser.parse(date_string)
    except (ValueError, TypeError):
        return None


def get_sort_params(allowed_fields):
    """
    Extract sort parameters from request args
    Returns: (sort_field, sort_direction)
    """
    sort_by = request.args.get('sort_by', allowed_fields[0] if allowed_fields else 'id')
    sort_order = request.args.get('sort_order', 'desc').lower()

    if sort_by not in allowed_fields:
        sort_by = allowed_fields[0] if allowed_fields else 'id'

    if sort_order not in ['asc', 'desc']:
        sort_order = 'desc'

    return sort_by, sort_order


def apply_sorting(query, model, sort_field, sort_direction):
    """
    Apply sorting to a query
    """
    if not hasattr(model, sort_field):
        return query

    field = getattr(model, sort_field)

    if sort_direction == 'asc':
        return query.order_by(field.asc())
    else:
        return query.order_by(field.desc())


def get_filter_params(allowed_filters):
    """
    Extract filter parameters from request args
    Returns: dict of {field: value}
    """
    filters = {}

    for filter_name in allowed_filters:
        value = request.args.get(filter_name)
        if value is not None:
            filters[filter_name] = value

    return filters

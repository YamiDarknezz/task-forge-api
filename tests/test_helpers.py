import pytest
from flask import Flask
from app.utils.helpers import (
    success_response,
    error_response,
    get_pagination_params,
    paginate,
    parse_date,
    get_sort_params,
    apply_sorting,
    get_filter_params
)
from app.models.task import Task
from datetime import datetime


class TestSuccessResponse:
    """Tests for success_response helper"""

    def test_success_response_with_data(self, app):
        """Test success response with data"""
        with app.app_context():
            response, status_code = success_response(data={'key': 'value'})
            assert status_code == 200
            assert response.json['success'] is True
            assert response.json['data'] == {'key': 'value'}

    def test_success_response_with_message(self, app):
        """Test success response with message"""
        with app.app_context():
            response, status_code = success_response(message='Operation successful')
            assert status_code == 200
            assert response.json['success'] is True
            assert response.json['message'] == 'Operation successful'

    def test_success_response_custom_status_code(self, app):
        """Test success response with custom status code"""
        with app.app_context():
            response, status_code = success_response(status_code=201)
            assert status_code == 201
            assert response.json['success'] is True


class TestErrorResponse:
    """Tests for error_response helper"""

    def test_error_response_basic(self, app):
        """Test basic error response"""
        with app.app_context():
            response, status_code = error_response('Error occurred')
            assert status_code == 400
            assert response.json['success'] is False
            assert response.json['message'] == 'Error occurred'

    def test_error_response_with_error_details(self, app):
        """Test error response with error details"""
        with app.app_context():
            response, status_code = error_response(
                'Error occurred',
                error={'field': 'invalid'},
                status_code=422
            )
            assert status_code == 422
            assert response.json['success'] is False
            assert response.json['error'] == {'field': 'invalid'}


class TestGetPaginationParams:
    """Tests for get_pagination_params helper"""

    def test_default_pagination(self, app, client):
        """Test default pagination parameters"""
        with app.test_request_context('/'):
            page, per_page, offset = get_pagination_params()
            assert page == 1
            assert per_page == app.config.get('DEFAULT_PAGE_SIZE', 10)
            assert offset == 0

    def test_custom_pagination(self, app):
        """Test custom pagination parameters"""
        with app.test_request_context('/?page=2&per_page=20'):
            page, per_page, offset = get_pagination_params()
            assert page == 2
            assert per_page == 20
            assert offset == 20

    def test_pagination_max_per_page(self, app):
        """Test pagination respects max_per_page"""
        with app.test_request_context('/?per_page=1000'):
            page, per_page, offset = get_pagination_params()
            max_per_page = app.config.get('MAX_PAGE_SIZE', 100)
            assert per_page == max_per_page

    def test_pagination_negative_values(self, app):
        """Test pagination with negative values"""
        with app.test_request_context('/?page=-1&per_page=-5'):
            page, per_page, offset = get_pagination_params()
            assert page == 1
            assert per_page == 10


class TestPaginate:
    """Tests for paginate helper"""

    def test_paginate_query(self, app, regular_user, sample_tasks):
        """Test paginating a query"""
        with app.app_context():
            query = Task.query.filter_by(user_id=regular_user.id)
            items, meta = paginate(query, page=1, per_page=2)

            assert len(items) == 2
            assert meta['page'] == 1
            assert meta['per_page'] == 2
            assert meta['total'] == 3
            assert meta['total_pages'] == 2
            assert meta['has_next'] is True
            assert meta['has_prev'] is False

    def test_paginate_last_page(self, app, regular_user, sample_tasks):
        """Test paginating last page"""
        with app.app_context():
            query = Task.query.filter_by(user_id=regular_user.id)
            items, meta = paginate(query, page=2, per_page=2)

            assert len(items) == 1
            assert meta['page'] == 2
            assert meta['has_next'] is False
            assert meta['has_prev'] is True


class TestParseDate:
    """Tests for parse_date helper"""

    def test_parse_valid_date(self):
        """Test parsing valid date strings"""
        date_strings = [
            '2024-01-15',
            '2024-01-15T10:30:00',
            '2024-01-15 10:30:00'
        ]
        for date_string in date_strings:
            result = parse_date(date_string)
            assert result is not None
            assert isinstance(result, datetime)

    def test_parse_invalid_date(self):
        """Test parsing invalid date"""
        result = parse_date('invalid-date')
        assert result is None

    def test_parse_empty_date(self):
        """Test parsing empty date"""
        result = parse_date('')
        assert result is None

    def test_parse_none_date(self):
        """Test parsing None date"""
        result = parse_date(None)
        assert result is None


class TestGetSortParams:
    """Tests for get_sort_params helper"""

    def test_default_sort_params(self, app):
        """Test default sort parameters"""
        with app.test_request_context('/'):
            sort_by, sort_order = get_sort_params(['id', 'created_at'])
            assert sort_by == 'id'
            assert sort_order == 'desc'

    def test_custom_sort_params(self, app):
        """Test custom sort parameters"""
        with app.test_request_context('/?sort_by=created_at&sort_order=asc'):
            sort_by, sort_order = get_sort_params(['id', 'created_at'])
            assert sort_by == 'created_at'
            assert sort_order == 'asc'

    def test_invalid_sort_field(self, app):
        """Test invalid sort field falls back to default"""
        with app.test_request_context('/?sort_by=invalid_field'):
            sort_by, sort_order = get_sort_params(['id', 'created_at'])
            assert sort_by == 'id'

    def test_invalid_sort_order(self, app):
        """Test invalid sort order falls back to default"""
        with app.test_request_context('/?sort_order=invalid'):
            sort_by, sort_order = get_sort_params(['id'])
            assert sort_order == 'desc'


class TestApplySorting:
    """Tests for apply_sorting helper"""

    def test_apply_sorting_asc(self, app, regular_user, sample_tasks):
        """Test applying ascending sort"""
        with app.app_context():
            query = Task.query.filter_by(user_id=regular_user.id)
            sorted_query = apply_sorting(query, Task, 'id', 'asc')
            tasks = sorted_query.all()

            assert tasks[0].id < tasks[-1].id

    def test_apply_sorting_desc(self, app, regular_user, sample_tasks):
        """Test applying descending sort"""
        with app.app_context():
            query = Task.query.filter_by(user_id=regular_user.id)
            sorted_query = apply_sorting(query, Task, 'id', 'desc')
            tasks = sorted_query.all()

            assert tasks[0].id > tasks[-1].id

    def test_apply_sorting_invalid_field(self, app, regular_user, sample_tasks):
        """Test applying sort with invalid field"""
        with app.app_context():
            query = Task.query.filter_by(user_id=regular_user.id)
            sorted_query = apply_sorting(query, Task, 'invalid_field', 'asc')

            # Should return query unchanged
            assert sorted_query is not None


class TestGetFilterParams:
    """Tests for get_filter_params helper"""

    def test_get_filter_params(self, app):
        """Test extracting filter parameters"""
        with app.test_request_context('/?status=completed&priority=high'):
            filters = get_filter_params(['status', 'priority'])
            assert filters == {'status': 'completed', 'priority': 'high'}

    def test_get_filter_params_partial(self, app):
        """Test extracting partial filter parameters"""
        with app.test_request_context('/?status=completed'):
            filters = get_filter_params(['status', 'priority'])
            assert filters == {'status': 'completed'}
            assert 'priority' not in filters

    def test_get_filter_params_none(self, app):
        """Test no filter parameters"""
        with app.test_request_context('/'):
            filters = get_filter_params(['status', 'priority'])
            assert filters == {}

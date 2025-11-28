import csv
import json
from io import StringIO
from flask import Response
from datetime import datetime


def export_to_csv(data, filename='export.csv', fields=None):
    """
    Export data to CSV format
    Args:
        data: List of dictionaries
        filename: Name of the file to download
        fields: List of field names to include (if None, uses all fields from first item)
    Returns:
        Flask Response with CSV file
    """
    if not data:
        return Response(
            'No data to export',
            mimetype='text/plain',
            status=404
        )

    if fields is None:
        fields = list(data[0].keys())

    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=fields, extrasaction='ignore')

    writer.writeheader()
    for row in data:
        clean_row = {}
        for key in fields:
            value = row.get(key, '')
            if isinstance(value, (list, dict)):
                value = json.dumps(value)
            elif value is None:
                value = ''
            clean_row[key] = value
        writer.writerow(clean_row)

    output.seek(0)

    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename={filename}'}
    )


def export_to_json(data, filename='export.json', pretty=True):
    """
    Export data to JSON format
    Args:
        data: Data to export (list or dict)
        filename: Name of the file to download
        pretty: Whether to format JSON with indentation
    Returns:
        Flask Response with JSON file
    """
    if pretty:
        json_str = json.dumps(data, indent=2, default=str)
    else:
        json_str = json.dumps(data, default=str)

    return Response(
        json_str,
        mimetype='application/json',
        headers={'Content-Disposition': f'attachment; filename={filename}'}
    )


def prepare_tasks_for_export(tasks):
    """
    Prepare task objects for export
    Flattens nested objects and formats dates
    """
    export_data = []

    for task in tasks:
        task_dict = task.to_dict(include_user=True, include_tags=True)

        flat_task = {
            'id': task_dict['id'],
            'title': task_dict['title'],
            'description': task_dict['description'],
            'status': task_dict['status'],
            'priority': task_dict['priority'],
            'due_date': task_dict['due_date'],
            'completed_at': task_dict['completed_at'],
            'is_overdue': task_dict['is_overdue'],
            'is_completed': task_dict['is_completed'],
            'created_at': task_dict['created_at'],
            'updated_at': task_dict['updated_at'],
            'user_id': task_dict['user_id'],
            'user_username': task_dict.get('user', {}).get('username', ''),
            'user_email': task_dict.get('user', {}).get('email', ''),
            'tags': ', '.join([tag['name'] for tag in task_dict.get('tags', [])])
        }

        export_data.append(flat_task)

    return export_data


def prepare_users_for_export(users):
    """
    Prepare user objects for export
    Excludes sensitive information
    """
    export_data = []

    for user in users:
        user_dict = user.to_dict(include_role=True)

        flat_user = {
            'id': user_dict['id'],
            'username': user_dict['username'],
            'email': user_dict['email'],
            'first_name': user_dict['first_name'],
            'last_name': user_dict['last_name'],
            'full_name': user_dict['full_name'],
            'is_active': user_dict['is_active'],
            'role': user_dict.get('role', {}).get('name', ''),
            'created_at': user_dict['created_at'],
            'updated_at': user_dict['updated_at']
        }

        export_data.append(flat_user)

    return export_data


def prepare_tags_for_export(tags):
    """
    Prepare tag objects for export
    """
    export_data = []

    for tag in tags:
        tag_dict = tag.to_dict(include_task_count=True)
        export_data.append(tag_dict)

    return export_data

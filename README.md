# Django Web App Lab 4

This repository contains a Django project built to demonstrate core web application concepts in a single, structured implementation.

## Project Overview

The main application (`django_demo`) is an article-focused platform where users can register, log in, create and manage articles, post comments, and customize viewing preferences. It is designed to illustrate:

- Request and response handling
- Form handling and validation
- Session and cookie usage
- URL routing and template rendering
- Middleware for logging, error handling, and security headers
- ORM-based CRUD operations
- Relational and semi-structured data modeling
- Authentication and authorization

## Technology Stack

- Python 3
- Django 6.0.3
- SQLite (development database)

## Setup and Run

From the `django_demo` directory:

```bash
python manage.py migrate
python manage.py runserver
```

Application URLs:

- `http://127.0.0.1:8000/` - Home
- `http://127.0.0.1:8000/articles/` - Article listing and search
- `http://127.0.0.1:8000/concepts/` - Concept demonstration page
- `http://127.0.0.1:8000/dashboard/` - Authenticated user dashboard

## Key Application Modules

- `core/models.py`: data models for categories, articles, comments, profiles, and event logs
- `core/views.py`: request handling, CRUD workflows, session/cookie logic, and API response
- `core/forms.py`: forms for authentication, article/comment input, profile, and preferences
- `core/middleware.py`: request logging, security headers, and exception handling
- `core/templates/core/`: template files for UI rendering
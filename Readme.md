# Taskflow AI

Taskflow AI is a Django project for managing tasks, clients, users, and core business operations.

## Project Structure

- `manage.py` - Django management script.
- `requirements.txt` - Python dependencies.
- `apps/` - Django apps:
  - `accounts` - authentication and profile management.
  - `clients` - client records and management.
  - `core` - dashboard, shared views, and application-wide features.
  - `tasks` - task management and services.
  - `users` - user administration.
- `config/` - Django application configuration and settings.
- `templates/` - HTML templates.
- `static/` - CSS, JavaScript, and public assets.
- `media/` - Uploaded files and media storage.

## Prerequisites

- Python 3.11+ (or compatible with `requirements.txt`).
- PostgreSQL database by default.
- `python-decouple` is used for `.env` configuration.

## Setup

1. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   .\.venv\Scripts\activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and update values:
   ```bash
   copy .env.example .env
   ```
4. Configure database and secret key in `.env`.
5. Run migrations:
   ```bash
   python manage.py migrate
   ```
6. Create a superuser for admin access:
   ```bash
   python manage.py createsuperuser
   ```
7. Collect static files for production:
   ```bash
   python manage.py collectstatic
   ```
8. Start the development server:
   ```bash
   python manage.py runserver
   ```

## `.env` Example

Use environment variables to configure the project. A sample `.env` file may include:

```env
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1
DB_NAME=taskflow_ai
DB_USER=postgres
DB_PASSWORD=your-db-password
DB_HOST=localhost
DB_PORT=5432
```

## XAMPP Notes

- This Django app runs independently from XAMPP's Apache/PHP stack.
- If you use XAMPP only for a database server, update the `.env` values to point to the correct host and port.
- The default database in this project is PostgreSQL, not MySQL.
- If you want to use MySQL/MariaDB from XAMPP, change `DATABASES` in `config/settings/base.py` and install the appropriate database driver.

## Running with a specific settings module

The project uses a `config/settings` package with environment-specific settings. For local development, ensure `DJANGO_SETTINGS_MODULE=config.settings.local` is set when running commands.

Example:
```bash
set DJANGO_SETTINGS_MODULE=config.settings.local
python manage.py runserver
```

## Common commands

- Run tests:
  ```bash
  python manage.py test
  ```
- Open Django shell:
  ```bash
  python manage.py shell
  ```
- Create or apply migrations:
  ```bash
  python manage.py makemigrations
  python manage.py migrate
  ```

## Notes

- Templates are located in `templates/` and app-specific subfolders.
- Static files are served from `static/` in development and `staticfiles/` after `collectstatic`.
- Uploaded media is stored in `media/`.

## 🤖 Local AI Core Setup (Ollama)

This project utilizes a local AI service layer for natural language task processing and workspace diagnostics.

1. Download and install **Ollama** on your machine from [ollama.com](https://ollama.com).
2. Pull the optimized coder model from your terminal before interacting with the system views:
   ```bash
   ollama pull qwen2.5-coder:3b
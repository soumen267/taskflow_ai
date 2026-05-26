# Taskflow AI

## 🚀 Core AI Features

TaskFlow AI stands out by integrating an entirely offline, local AI intelligence layer leveraging **Ollama (`qwen2.5-coder:3b`)**, eliminating cloud API dependencies:

- **🤖 AI Task Flow Quick Add:** Parses unstructured, conversational English sentences (e.g., *"Fix database connection issues by Friday afternoon for Client 2 assign to soumen12"*) and automatically validates, maps, and creates structured database records.
- **💡 AI Workspace Copilot:** A role-aware dashboard diagnostic engine:
  - *For Team Members:* Generates personalized morning focus briefings, critical priorities, and overdue target highlights.
  - *For Administrators:* Shifts into an executive operations dashboard manager, auto-aggregating across all team members to pinpoint productivity bottlenecks and workflow risks.

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

## 🌐 Production Deployment Notes

When transitioning from local development to a live production server, ensure the following configurations are updated:

### 1. Environment Adjustments (`.env`)
- Change `DEBUG=False` in your production environment variables to turn off error tracebacks and disable the Django Debug Toolbar (`DjDT`).
- Generate a unique, secure `SECRET_KEY` specifically for production.
- Update `ALLOWED_HOSTS` to include your live domain name (e.g., `ALLOWED_HOSTS=your-app.com,your-subdomain.onrender.com`).

### 2. Static Files (`WhiteNoise`)
This project uses **WhiteNoise** to serve static assets. Before running the production server, compile and collect all your CSS, JavaScript, and asset layers into the main deployment directory:
```bash
python manage.py collectstatic --noinput

### 🐳 Running with Docker

If you prefer to use Docker instead of setting up Python and PostgreSQL manually on your host machine:

1. Ensure **Docker Desktop** is installed and running on your system.
2. Build and launch the container ecosystem:
   ```bash
   docker-compose up --build
3. Run migrations inside the active web container to build your tables:
    docker-compose exec web python manage.py migrate
4. Create your admin/superuser account:
    docker-compose exec web python manage.py createsuperuser
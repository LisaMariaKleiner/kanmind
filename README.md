# KanMind Backend

This repository contains the backend for the KanMind project, built with Django and Django REST Framework.

## Requirements

- Python 3.8+
- Django 4.x
- djangorestframework

## Setup Instructions

1. **Clone the repository:**

   ```bash
   git clone <your-backend-repo-url>
   cd backend
   ```

2. **Create a virtual environment (recommended):**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Apply migrations:**

   ```bash
   python manage.py migrate
   ```

5. **Create a superuser (optional, for admin access):**

   ```bash
   python manage.py createsuperuser
   ```

6. **Run the development server:**

   ```bash
   python manage.py runserver
   ```

7. **Access the API:**
   - The API will be available at `http://localhost:8000/`

## Project Structure

- `core/` – Django project settings and configuration
- `authentication/` – User authentication app
- `boards/` – Boards management app
- `tasks/` – Tasks management app

## Important Notes

- **Never commit your database file (`db.sqlite3`) or secret keys to the repository.**
- All environment variables and secrets should be stored in a `.env` file (not tracked by git).
- For any special configurations or deployment notes, see the comments in `settings.py`.

## License

See [LICENSE](LICENSE) for details.

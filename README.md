# Videoflix Backend

Videoflix is a backend service designed for a video streaming platform, built with Django. It offers a range of features including user registration, password recovery, video management, and additional functionalities to support video streaming operations.

## Features

- **User Management:** Registration, login, and password reset.
- **Video Management:** Upload, management, and retrieval of video content.
- **Background Tasks:** Background processes for tasks like video encoding via RQWorker.
- **Security:** Authentication and authorization using JWT (JSON Web Tokens).
- **Email Notifications:** Send emails for registration and password reset.

## Prerequisites

To run this backend locally, make sure you have the following tools installed:

- [Python 3.9+](https://www.python.org/downloads/)
- [PostgreSQL](https://www.postgresql.org/download/)
- [Redis](https://redis.io/download)
- [FFmpeg](https://ffmpeg.org/download.html)
- [Git](https://git-scm.com/)
- [Virtualenv](https://virtualenv.pypa.io/en/latest/)

## Installation

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/your-username/videoflix-backend.git
   cd videoflix-backend

2. **Create and activate a virtual environment:**
   If you don't have virtualenv installed, you can install it with pip install virtualenv.
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   
3. **Install the dependencies**
   ```bash
   pip install -r requirements.txt

4. **Set up PostgreSQL:**
   Install PostgreSQL and create a database for the project.
   Create a PostgreSQL user and database. You can do this by running the following in psql:
   ```sql
   CREATE DATABASE videoflix;
   CREATE USER videoflix_user WITH PASSWORD 'yourpassword';
   ALTER ROLE videoflix_user SET client_encoding TO 'utf8';
   ALTER ROLE videoflix_user SET default_transaction_isolation TO 'read committed';
   ALTER ROLE videoflix_user SET timezone TO 'UTC';
   GRANT ALL PRIVILEGES ON DATABASE videoflix TO videoflix_user;

5. **Set up th environment variables:**
   Create a .env file in the root of the project and add the following environment variables:
   ```ini
   # Email settings for sending emails (e.g., for user registration, password reset, etc.)
   EMAIL_HOST=smtp.email-provider.com          # SMTP server address (e.g., Gmail, SendGrid)
   EMAIL_PORT=587                             # SMTP server port (587 is typically for TLS)
   EMAIL_HOST_USER=youremail@yourdomain.com   # Your email account for sending emails
   EMAIL_HOST_PASSWORD=yourpassword           # The password for the above email account
   DEFAULT_FROM_EMAIL=youremail@yourdomain.com # Default email address used in 'From' field

   # Redis settings for background task queue (RQWorker)
   REDIS_PASSWORD=password                    # Password for the Redis instance (if applicable)

   # PostgreSQL settings for connecting to the database
   POSTRQL_USER=user                          # PostgreSQL database user
   POSTRQL_PASSWORD=password                  # Password for the PostgreSQL user

   # If you're using a different environment for RQWorker on Windows (VENV), specify here
   ENV_LIN_HOST=your.server.ip                # This is the IP address or hostname for your server

   # Frontend URL, used for building API endpoints or sending email links (e.g., password reset)
   FRONTEND_URL=http://localhost:4200/         # URL of your frontend (in this case, local development server)

6. **Install FFmpeg:**
   Install FFmpeg for video processing (for example, for encoding videos). Follow the installation guide for your operating system.

7. **Migrate the database:**
   Run the migrations to set up the database schema:
   ```bash
   python manage.py makemigrations
   python manage.py migrate

8. **Create a Superuser:**
   To create an admin superuser, run the following command:
   ```bash
   python manage.py createsuperuser

   Follow the prompts to create the superuser.

9. **Start the Redis server**
   If Redis is not running, start it by running:
    ```bash
    redis-server

10. **Start the RQ Worker:**
    RQWorker is used for background tasks (like video encoding). In one terminal, start the worker:
    ```bash
    python manage.py rqworker

11. **Run the Django Development Server**
    Finally, start the Django server to run the API:
    ````bash
    python manage.py runserver

   The server should now be running at http://127.0.0.1:8000.







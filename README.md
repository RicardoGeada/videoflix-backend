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

2. **Create and activate a virtual environment**
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



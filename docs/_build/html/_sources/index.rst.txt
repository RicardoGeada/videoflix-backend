.. videoflix_backend documentation master file, created by
   sphinx-quickstart on Sat Nov 16 02:43:01 2024.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

videoflix_backend documentation
===============================

Videoflix is a backend service designed for a video streaming platform, built with Django. 
It offers a range of features including user registration, password recovery, video management, and additional functionalities to support video streaming operations.

Features
========
* User Management: Registration, login, and password reset.
* Video Management: Upload, management, and retrieval of video content.
* Background Tasks: Background processes for tasks like video encoding via RQWorker.
* Security: Authentication and authorization using JWT (JSON Web Tokens).
* Email Notifications: Send emails for registration and password reset.


.. toctree::
   :maxdepth: 2
   :caption: Contents:

   installation.rst
   videoflix_backend.rst
   content.rst
   users.rst
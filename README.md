# Edu-site

Edu-site is a comprehensive web application designed to facilitate online learning and education. It offers a range of features including video playback, user management, and course creation. The application is built using Flask, a Python web framework, and integrates various libraries and tools to deliver a seamless user experience.

## Features
- **Video Playback**: Watch and manage educational videos with support for viewing recommendations.
- **User Management**: Admin functionalities for user account management including creation, editing, and deactivation.
- **Course Creation**: Create and manage different types of educational content such as courses, blogs, and articles.
- **Responsive Design**: Optimized for both desktop and mobile views to ensure accessibility across devices.
- **Interactive Elements**: Includes forms for creating blogs and courses, and other interactive elements to engage users.

## Technologies Used
- Flask
- SQLAlchemy
- Flask-Bootstrap
- Flask-Login
- Flask-Migrate
- Flask-SQLAlchemy
- Flask-WTF
- Jinja2
- HTML/CSS
- JavaScript

## Installation

To get started with Edu-site, follow these steps to set up the project on your local machine.

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Clone the Repository
First, clone the repository from GitHub:
```bash
git clone https://github.com/abdurehman760/Edu-site/
cd Edu-site
```

### Install Dependencies
Create a virtual environment and install the required packages:
```
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
pip install -r requirements.txt
```
### Set Up the Database
Initialize the database:
```
flask db upgrade
```
### Run the Application
Start the development server:
```
flask run
```
The application will be accessible at http://127.0.0.1:5000/.

This ensures that the headings and code blocks are formatted correctly for easy readability and copying.


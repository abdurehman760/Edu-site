# Edu-site

Edu-site is a comprehensive web application designed to facilitate online learning and education. It offers a range of features including video playback, user management, and course creation. The application is built using Flask, a Python web framework, and integrates various libraries and tools to deliver a seamless user experience.

## Features

Edu-site is a versatile educational platform equipped with various features to enhance user experience and content management. Here’s a detailed overview of its key features:

### 1. User Management
- **Admin Dashboard**: Comprehensive interface for managing user accounts, including editing, deactivating, and deleting users.
- **User Roles**: Flexible role management allows admins to assign and modify user roles.

### 2. Video Management
- **Video Playback**: Stream videos with an intuitive player interface and integrated controls.
- **Suggested Videos**: Automatically recommend videos from the same category based on user interests.
- **Thumbnail Generation**: Generate and manage video thumbnails automatically.

### 3. Content Creation and Management
- **Dynamic Course Creation**: Create and manage courses dynamically with real-time updates and content management.
- **Dynamic Category Creation**: Add and manage categories for courses and content on the fly.
- **Built-in Courses**: Access pre-defined courses that come with the platform for quick deployment.

### 4. Messaging System
- **User Messaging**: Send, receive, and manage messages between users within the platform.
- **Message Viewing**: View message history and track conversations.

### 5. Blog Management
- **Blog Creation**: Publish blog posts with a rich text editor, including multimedia content.
- **Blog Listings**: Display a list of all blog posts with summaries and access to individual posts.

### 6. Course Management
- **Course Listings**: View a comprehensive list of available courses with detailed descriptions.
- **Course Details**: Access detailed information about each course, including curriculum and instructor details.

### 7. Interactive Features
- **Comments**: Users can comment on videos and blog posts, facilitating interaction and feedback.
- **User Interaction**: Engage with dynamic content through user comments and feedback.

### 8. Localization and Accessibility
- **Multilingual Support**: The platform supports multiple languages to cater to a diverse audience.
- **Responsive Design**: Modern, responsive layout ensures a seamless experience across various devices.




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

HAVE fun



from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify,json
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
from sqlalchemy.sql import func
from sqlalchemy import func
import pytz
import uuid
import os
import json 
from werkzeug.utils import secure_filename
from sqlalchemy.orm import relationship








app = Flask(__name__)
app.template_folder = 'templates'
app.secret_key = 'secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'



upload_folder_video = os.path.join(app.root_path, 'static', 'upload_video')
upload_folder_images = os.path.join(app.root_path, 'static', 'upload_images')
upload_folder_thumbnail = os.path.join(app.root_path, 'static', 'upload_thumbnail')
upload_folder_attachments = os.path.join(app.root_path, 'static', 'upload_attachments')

app.config['UPLOAD_FOLDER_VIDEO'] = upload_folder_video
app.config['UPLOAD_FOLDER_IMAGES'] = upload_folder_images
app.config['UPLOAD_FOLDER_THUMBNAIL'] = upload_folder_thumbnail
app.config['UPLOAD_FOLDER_ATTACHMENTS'] = upload_folder_attachments

# Define allowed file extensions
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mkv', 'mov', 'flv', 'jpg', 'svg', 'jpeg', 'png', 'gif', 'webp', 'pdf', 'docx', 'doc'}
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



app.config['TIMEZONE'] = pytz.timezone('Asia/Karachi')
db = SQLAlchemy()
db.init_app(app)
migrate = Migrate(app, db)

# Define the User model
class users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    role = db.Column(db.String(20), default='user')
    profile_picture = db.Column(db.String(255), default='avatar.avif')
    uuid = db.Column(db.String(36), unique=True, nullable=False, default=str(uuid.uuid4()))
    status = db.Column(db.String(20), default='active')
    created_at = db.Column(db.DateTime, default=db.func.now())
    deactivated_at = db.Column(db.DateTime, default=None)  # Change the default value
    videos = db.relationship('Video', backref='users', lazy=True)
    liked_videos = db.relationship('VideoLike', backref='user', lazy=True)
    

    def __repr__(self):
        return f"{self.id}-{self.username}"
    

    
class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    description = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    file_path = db.Column(db.String(100))
    category = db.Column(db.String(50))
    video_thumbnail = db.Column(db.String(100))
    upload_time = db.Column(db.DateTime, default=datetime.utcnow)
    views = db.Column(db.Integer, default=0)
    likes_count = db.Column(db.Integer, default=0)  # New column to store likes count
    dislikes_count = db.Column(db.Integer, default=0)

    likes = db.relationship('VideoLike', backref='video', lazy=True)
    dislikes = db.relationship('VideoDislike', backref='video', lazy=True)

    def update_likes_count(self):
        self.likes_count = len(self.likes)

    def calculate_unique_likes(self):
        unique_likes_query = db.session.query(func.count(VideoLike.user_id.distinct())).filter_by(video_id=self.id)
        self.likes_count = unique_likes_query.scalar()

    def calculate_unique_dislikes(self):
        unique_dislikes_query = db.session.query(func.count(VideoDislike.user_id.distinct())).filter_by(video_id=self.id)
        self.dislikes_count = unique_dislikes_query.scalar()

class VideoLike(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    video_id = db.Column(db.Integer, db.ForeignKey('video.id'), nullable=False)

class VideoDislike(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    video_id = db.Column(db.Integer, db.ForeignKey('video.id'), nullable=False)


    
    

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    thumbnail_url = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50))
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    creation_timestamp = db.Column(db.DateTime, default=db.func.now())




class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    course_mention = db.Column(db.String(100), default='none') 
    user = db.relationship('users', backref=db.backref('comments', lazy=True))

    def __init__(self, name, email, message, user_id=None, course_mention='none'):
        self.name = name
        self.email = email
        self.message = message
        self.user_id = user_id
        self.course_mention = course_mention 

class Reply(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.now())
    comment_id = db.Column(db.Integer, db.ForeignKey('comment.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))  # Add a user_id column

 
    user = relationship('users')

    def __init__(self, message, comment_id, user_id):
        self.message = message
        self.comment_id = comment_id
        self.user_id = user_id



class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(50), nullable=False)
    thumbnail_filename = db.Column(db.String(255), nullable=False)
    cover_pic_filename  = db.Column(db.String(255), nullable=False)
    attachments_filename  = db.Column(db.String(255))
    content = db.Column(db.Text, nullable=False)
    blog_category= db.Column(db.String(50), nullable=False)
    custom_category = db.Column(db.String(50))
    keywords = db.Column(db.String(100))
    is_featured = db.Column(db.Boolean, default=False)
    status = db.Column(db.String(20), default='draft')
    posted_at = db.Column(db.DateTime)
    archived_at = db.Column(db.DateTime)
    published_at = db.Column(db.DateTime)
    user_uuid = db.Column(db.String(36), db.ForeignKey('users.uuid'), nullable=False)
    user = db.relationship('users', backref=db.backref('blog_posts', lazy=True))
    comments = db.relationship('BlogComment', backref='blog_post', lazy='dynamic')

class BlogComment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('users', foreign_keys=[user_id])
    blog_post_id = db.Column(db.Integer, db.ForeignKey('blog_post.id'))
    replies = db.relationship('BlogReply', backref='comment', lazy='dynamic')
    

    def __init__(self, name, email, message, user_id=None, blog_post_id=None, course_mention=None):
        self.name = name
        self.email = email
        self.message = message
        self.user_id = user_id
        self.blog_post_id = blog_post_id 
        self.course_mention = course_mention

class BlogReply(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    comment_id = db.Column(db.Integer, db.ForeignKey('blog_comment.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('users', foreign_keys=[user_id])

    def __init__(self, message, comment_id, user_id):
        self.message = message
        self.comment_id = comment_id
        self.user_id = user_id


class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    teacher_mentioned_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    name = db.Column(db.String(100), nullable=False)  # Add 'name' column
    user_email = db.Column(db.String(80), nullable=False)  # Add 'user_email' column
    subject = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.now())
    user = db.relationship('users', foreign_keys=[user_id], backref='contacts')
    teacher_mentioned = db.relationship('users', foreign_keys=[teacher_mentioned_id])





    





with app.app_context():
    db.create_all()

# Define the get_current_user function
def get_current_user():
    if 'user_id' in session:
        user_id = session['user_id']
        user = users.query.get(user_id)
        return user
    else:
        return None  # Return None if the user is not logged in
    

@app.route('/')
def index():
    return render_template('Navbar/index.html')
    

@app.route('/like_video/<int:video_id>', methods=['POST'])
def like_video(video_id):
    user = get_current_user()
    if not user:
        return jsonify({"message": "You must be logged in to like videos."}), 403

    video = Video.query.get(video_id)

    if not video:
        return jsonify({"message": "Video not found."}), 404

    existing_like = VideoLike.query.filter_by(user_id=user.id, video_id=video.id).first()

    if existing_like:
        return jsonify({"message": "You have already liked this video."}), 400

    # Create a new VideoLike entry to represent the like
    like = VideoLike(user_id=user.id, video_id=video.id)
    db.session.add(like)
    db.session.commit()

    # Calculate the unique likes for the video
    video.calculate_unique_likes()
    db.session.commit()

    return jsonify({"message": "Video liked successfully."}), 200



@app.route('/dislike_video/<int:video_id>', methods=['POST'])
def dislike_video(video_id):
    user = get_current_user()
    if not user:
        return jsonify({"message": "You must be logged in to dislike videos."}), 403

    video = Video.query.get(video_id)

    if not video:
        return jsonify({"message": "Video not found."}), 404

    existing_like = VideoLike.query.filter_by(user_id=user.id, video_id=video.id).first()
    existing_dislike = VideoDislike.query.filter_by(user_id=user.id, video_id=video.id).first()

    if existing_like:
        return jsonify({"message": "You have already liked this video. You can't dislike it."}), 400

    if existing_dislike:
        return jsonify({"message": "You have already disliked this video."}), 400

    # Create a new VideoDislike entry to represent the dislike
    dislike = VideoDislike(user_id=user.id, video_id=video.id)
    db.session.add(dislike)
    db.session.commit()

    # Calculate the unique dislikes for the video
    video.calculate_unique_dislikes()
    db.session.commit()

    return jsonify({"message": "Video disliked successfully."}), 200









@app.route('/create_course', methods=['GET', 'POST'])
def create_course():
    # Check if the user is logged in
    user = get_current_user()
    if user is None:
        return redirect(url_for('login'))

    # Check if the user has the 'teacher' role
    if user.role not in ['teacher', 'admin']:
        flash('You do not have permission to access the course creation form.', 'error')
        return redirect(url_for('login'))  

    if request.method == 'POST':
        name = request.form['course_name']
        category = request.form['category']
        thumbnail = request.files['thumbnail']

        if name and thumbnail:
            counter = 1
            file_extension = os.path.splitext(thumbnail.filename)[1]
            while os.path.exists(os.path.join(app.config['UPLOAD_FOLDER_IMAGES'], generate_course_thumbnail_filename(counter, file_extension))):
                counter += 1
            thumbnail_filename = generate_course_thumbnail_filename(counter, file_extension)
            thumbnail.save(os.path.join(app.config['UPLOAD_FOLDER_IMAGES'], thumbnail_filename))

            new_course = Course(name=name, thumbnail_url=os.path.join('static', 'upload_images', thumbnail_filename), category=category, creator_id=user.id)
            db.session.add(new_course)
            db.session.commit()

            flash('Course created successfully', 'success')
        else:
            flash('Please provide a course name and thumbnail', 'error')

        return redirect(url_for('create_course'))

    return render_template('Dashboards/create_course.html')


def generate_course_thumbnail_filename(counter, file_extension):
    return f"course_thumbnail_{counter}{file_extension}"


@app.route('/delete_course/<int:course_id>', methods=['POST'])
def delete_course(course_id):
    # Fetch the course to be deleted from the database
    course = Course.query.get(course_id)

    if course:
        # Check if the current user is an "admin" or the course creator
        user = get_current_user()  

        if user and (user.role == 'admin' or user.id == course.creator_id):
            # Delete the associated thumbnail image from the filesystem
            thumbnail_path = os.path.join(app.config['UPLOAD_FOLDER_IMAGES'], course.thumbnail_url.split("/")[-1])
            if os.path.exists(thumbnail_path):
                os.remove(thumbnail_path)

            # Delete the course from the database
            db.session.delete(course)
            db.session.commit()

            flash('Course and thumbnail deleted successfully', 'success')
        else:
            flash('You do not have permission to delete this course', 'error')
    else:
        flash('Course not found', 'error')

    return redirect(url_for('course'))







@app.route('/course/<int:course_id>')
def course_details(course_id):
    user=get_current_user()
    course = Course.query.get(course_id)
    videos = Video.query.filter_by(category=course.category).all()
    return render_template('Courses/course_details.html',user=user, course=course, videos=videos)



@app.route('/delete_video/<int:video_id>/<int:course_id>', methods=['POST'])
def delete_video(video_id, course_id):
    user = get_current_user()
    if user is None or user.role != 'teacher':
        flash('You do not have permission to delete videos.', 'error')
        return redirect(url_for('course_details', course_id=course_id))  # Redirect to the course details page

    # Fetch the video to be deleted from the database
    video = Video.query.get(video_id)

    if video:
        # Check if the user is the course creator
        if user.id == video.user_id:
            # Delete the video from the database
            db.session.delete(video)
            db.session.commit()
            flash('Video deleted successfully', 'success')
        else:
            flash('You do not have permission to delete this video', 'error')
    else:
        flash('Video not found', 'error')

    return redirect(url_for('course_details', course_id=course_id))









@app.route('/post_comment', methods=['POST'])
def post_comment():
    user = get_current_user()

    if user is None:
        flash('You must be logged in to post a comment.', 'error')
        return redirect(url_for('login'))

    message = request.form['message']
    parent_comment_id = request.form.get('parent_comment_id')  # Get the parent comment ID
    course_mention = request.form.get('course_mention')  # Get the course mention

    if message:
        comment = Comment(name=user.username, email=user.email, message=message, user_id=user.id, course_mention=course_mention)
        db.session.add(comment)

        if parent_comment_id:
            parent_comment = Comment.query.get(parent_comment_id)
            if parent_comment:
                comment.parent = parent_comment

        db.session.commit()
        flash('Comment/reply posted successfully!', 'success')
    else:
        flash('Please fill in the message field to post a comment/reply.', 'error')

    return redirect(url_for('course'))

@app.route('/post_reply', methods=['POST'])
def post_reply():
    if 'user_id' in session:
        user_id = session['user_id']
        user = users.query.get(user_id)

        if user:
            comment_id = request.form.get('comment_id')
            message = request.form.get('reply_message')

            if comment_id and message:
                reply = Reply(message=message, comment_id=comment_id, user_id=user.id)
                db.session.add(reply)
                db.session.commit()
                flash('Reply posted successfully!', 'success')
            else:
                flash('Invalid data. Please provide both a comment ID and a message for the reply.', 'error')

            return redirect(url_for('course'))  # Redirect to the comments page or any other appropriate page
        else:
            flash('User not found. Please log in to post a reply.', 'error')
    else:
        flash('Please log in to post a reply.', 'error')

    return redirect(url_for('login'))  # Redirect to the login page or any other appropriate page
    

def generate_course_thumbnail_filename(counter, file_extension):
    return f"course_thumbnail_{counter}{file_extension}"



@app.route('/delete_comment/<int:comment_id>', methods=['GET', 'POST'])
def delete_comment(comment_id):
    user = get_current_user()

    if user is None:
        flash('You do not have permission to delete comments. Please log in first.', 'error')
        return redirect(url_for('login'))

    comment = Comment.query.get(comment_id)

    if comment is None:
        flash('Comment not found.', 'error')
        return redirect(url_for('course'))

    if user.id == comment.user_id or user.role == 'teacher':
        # Check if the user is the owner of the comment or a teacher

        # Delete associated replies
        replies = Reply.query.filter_by(comment_id=comment_id).all()
        for reply in replies:
            db.session.delete(reply)

        # Delete the comment
        db.session.delete(comment)
        db.session.commit()
        flash('Comment and associated replies deleted successfully.', 'success')
    else:
        flash('You do not have permission to delete this comment.', 'error')

    return redirect(url_for('course'))



@app.route('/delete_reply/<int:reply_id>',methods=['GET', 'POST'])
def delete_reply(reply_id):
    user = get_current_user()

    if user is None:
        flash('You do not have permission to delete replies. Please log in first.', 'error')
        return redirect(url_for('login'))

    reply = Reply.query.get(reply_id)

    if reply is None:
        flash('Reply not found.', 'error')
        return redirect(url_for('course'))

    comment = Comment.query.get(reply.comment_id)

    if user.id == reply.user_id or (user.role == 'teacher' and user.id == comment.user_id):
        # Check if the user is the owner of the reply or a teacher who can delete replies
        db.session.delete(reply)
        db.session.commit()
        flash('Reply deleted successfully.', 'success')
    else:
        flash('You do not have permission to delete this reply.', 'error')

    return redirect(url_for('course'))




@app.route('/edit_comment/<int:comment_id>', methods=['POST'])
def edit_comment(comment_id):
    user = get_current_user()

    if user is None:
        flash('You do not have permission to edit comments. Please log in first.', 'error')
        return redirect(url_for('login'))

    comment = Comment.query.get(comment_id)

    if comment is None:
        flash('Comment not found.', 'error')
        return redirect(url_for('course'))

    if user.id != comment.user_id:
        flash('You do not have permission to edit this comment.', 'error')
        return redirect(url_for('course'))

    if request.method == 'POST':
        edited_message = request.form.get('edited_message')
        if edited_message:
            comment.message = edited_message
            db.session.commit()
            flash('Comment edited successfully.', 'success')
        else:
            flash('Please provide a valid comment.', 'error')

    return redirect(url_for('course'))

@app.route('/edit_reply/<int:reply_id>', methods=[ 'POST'])
def edit_reply(reply_id):
    user = get_current_user()

    if user is None:
        flash('You do not have permission to edit replies. Please log in first.', 'error')
        return redirect(url_for('login'))

    reply = Reply.query.get(reply_id)

    if reply is None:
        flash('Reply not found.', 'error')
        return redirect(url_for('course'))

    if user.id == reply.user_id:
        # Check if the user is the owner of the reply

        if request.method == 'POST':
            edited_message = request.form.get('edited_message')
            if edited_message:
                reply.message = edited_message
                db.session.commit()
                flash('Reply edited successfully.', 'success')
            else:
                flash('Please provide a valid reply.', 'error')

    return redirect(url_for('course'))


from sqlalchemy.orm import joinedload



from sqlalchemy.orm import joinedload

@app.route('/blog_post/<int:post_id>', methods=['GET', 'POST'])
def blog_post(post_id):
    user = get_current_user()
    if user is None:
        flash('You do not have permission to access the Blog page. Log in first', 'error')
        return redirect(url_for('login'))

    post = BlogPost.query.filter_by(id=post_id).first_or_404()

    # Separate query for comments with eager loading of the user relationship
    comments = (
        BlogComment.query
        .filter_by(blog_post_id=post_id)
        .options(joinedload(BlogComment.user))
        .all()
    )

    if request.method == 'POST':
        message = request.form.get('message')
        comment_id = request.form.get('comment_id')  # For replies

        if message:
            if comment_id:
                # This is a reply
                blog_reply = BlogReply(message=message, comment_id=comment_id, user_id=user.id)
                db.session.add(blog_reply)
            else:
                # This is a new comment
                blog_comment = BlogComment(name=user.username, email=user.email, message=message, user_id=user.id, blog_post_id=post.id)
                db.session.add(blog_comment)

            db.session.commit()
            flash('Comment/reply posted successfully!', 'success')
            return redirect(url_for('blog_post', post_id=post.id))

    return render_template('Blogs/blog_post.html', post=post, user=user, comments=comments)




@app.route('/post_blog_comment', methods=['POST'])
def post_blog_comment():
    user = get_current_user()

    if user is None:
        flash('You must be logged in to post a blog comment.', 'error')
        return redirect(url_for('login'))

    message = request.form['message']
    blog_post_id = request.form.get('blog_post_id')  # Get the blog post ID

    if message:
        blog_comment = BlogComment(name=user.username, email=user.email, message=message, user_id=user.id, blog_post_id=blog_post_id)
        db.session.add(blog_comment)
        db.session.commit()
        flash('Blog comment posted successfully!', 'success')
    else:
        flash('Please fill in the message field to post a blog comment.', 'error')

    return redirect(url_for('blog_post', blog_post_id=blog_post_id))

@app.route('/post_blog_reply', methods=['POST'])
def post_blog_reply():
    if 'user_id' in session:
        user_id = session['user_id']
        user = users.query.get(user_id)

        if user:
            comment_id = request.form.get('comment_id')
            message = request.form.get('reply_message')

            if comment_id and message:
                blog_reply = BlogReply(message=message, comment_id=comment_id, user_id=user.id)
                db.session.add(blog_reply)
                db.session.commit()
                flash('Blog reply posted successfully!', 'success')
            else:
                flash('Invalid data. Please provide both a comment ID and a message for the blog reply.', 'error')

            return redirect(url_for('blog_post', blog_post_id=blog_reply.comment.blog_post_id))  # Redirect to the blog post page or any other appropriate page
        else:
            flash('User not found. Please log in to post a blog reply.', 'error')
    else:
        flash('Please log in to post a blog reply.', 'error')

    return redirect(url_for('login'))  # Redirect to the login page or any other appropriate page

@app.route('/delete_blog_comment/<int:comment_id>', methods=['GET', 'POST'])
def delete_blog_comment(comment_id):
    user = get_current_user()

    if user is None:
        flash('You do not have permission to delete blog comments. Please log in first.', 'error')
        return redirect(url_for('login'))

    blog_comment = BlogComment.query.get(comment_id)

    if blog_comment is None:
        flash('Blog comment not found.', 'error')
        return redirect(url_for('blog'))

    if user.id == blog_comment.user_id or user.role == 'teacher':
        # Check if the user is the owner of the blog comment or a teacher

        # Delete associated blog replies
        blog_replies = BlogReply.query.filter_by(comment_id=comment_id).all()
        for blog_reply in blog_replies:
            db.session.delete(blog_reply)

        # Delete the blog comment
        db.session.delete(blog_comment)
        db.session.commit()
        flash('Blog comment and associated replies deleted successfully.', 'success')
    else:
        flash('You do not have permission to delete this blog comment.', 'error')

    return redirect(url_for('blog_post', post_id=blog_comment.blog_post_id))



@app.route('/delete_blog_reply/<int:reply_id>',methods=['GET', 'POST'])
def delete_blog_reply(reply_id):
    user = get_current_user()

    if user is None:
        flash('You do not have permission to delete blog replies. Please log in first.', 'error')
        return redirect(url_for('login'))

    blog_reply = BlogReply.query.get(reply_id)

    if blog_reply is None:
        flash('Blog reply not found.', 'error')
        return redirect(url_for('blog'))

    blog_comment = BlogComment.query.get(blog_reply.comment_id)

    if user.id == blog_reply.user_id or (user.role == 'teacher' and user.id == blog_comment.user_id):
        # Check if the user is the owner of the blog reply or a teacher who can delete blog replies
        db.session.delete(blog_reply)
        db.session.commit()
        flash('Blog reply deleted successfully.', 'success')
    else:
        flash('You do not have permission to delete this blog reply.', 'error')

    return redirect(url_for('blog_post', post_id=blog_reply.comment.blog_post_id))





@app.route('/edit_blog_comment/<int:comment_id>', methods=['POST'])
def edit_blog_comment(comment_id):
    user = get_current_user()

    if user is None:
        flash('You do not have permission to edit blog comments. Please log in first.', 'error')
        return redirect(url_for('login'))

    blog_comment = BlogComment.query.get(comment_id)

    if blog_comment is None:
        flash('Blog comment not found.', 'error')
        return redirect(url_for('blog'))

    if user.id != blog_comment.user_id:
        flash('You do not have permission to edit this blog comment.', 'error')
        return redirect(url_for('blog'))

    if request.method == 'POST':
        edited_message = request.form.get('edited_message')
        if edited_message:
            blog_comment.message = edited_message
            db.session.commit()
            flash('Blog comment edited successfully.', 'success')
        else:
            flash('Please provide a valid blog comment.', 'error')

    return redirect(url_for('blog_post', post_id=blog_comment.blog_post_id))




@app.route('/edit_blog_reply/<int:reply_id>', methods=[ 'POST'])
def edit_blog_reply(reply_id):
    user = get_current_user()

    if user is None:
        flash('You do not have permission to edit blog replies. Please log in first.', 'error')
        return redirect(url_for('login'))

    blog_reply = BlogReply.query.get(reply_id)

    if blog_reply is None:
        flash('Blog reply not found.', 'error')
        return redirect(url_for('blog'))

    if user.id == blog_reply.user_id:
        # Check if the user is the owner of the blog reply

        if request.method == 'POST':
            edited_message = request.form.get('edited_message')
            if edited_message:
                blog_reply.message = edited_message
                db.session.commit()
                flash('Blog reply edited successfully.', 'success')
            else:
                flash('Please provide a valid blog reply.', 'error')

    return redirect(url_for('blog_post', post_id=blog_reply.comment.blog_post_id))






    
@app.route('/about')
def about():
    return render_template('Navbar/about.html')

@app.route('/course')
def course():
    user = get_current_user()
    if user is None:
        flash('You do not have permission to access the Course page. Please log in first.', 'error')
        return redirect(url_for('login'))
    courses = Course.query.all()
    # Query all comments, ordering them by the timestamp in descending order
    comments = Comment.query.order_by(Comment.timestamp.desc()).all()

    # Query associated replies for each comment
    for comment in comments:
        comment.replies = Reply.query.filter_by(comment_id=comment.id).all()
    categories = Course.query.with_entities(Course.category, Course.creator_id).distinct().all()

    return render_template('Navbar/course.html', user=user, comments=comments, courses=courses,categories=categories)



@app.route('/blog')
def blog():
    user = get_current_user()
    if user is None:
        flash('You do not have permission to access the Blog page. Please login first.', 'error')
        return redirect(url_for('login'))

    # Assuming you have a function to query and retrieve blog posts from the database
    page = request.args.get('page', 1, type=int)  # Get the page number from the query parameters

    # Set the number of blog posts per page
    per_page = 3  # You can adjust this based on your preference

    # Query and paginate all blog posts, sorted by posted_at in descending order
    blog_posts = BlogPost.query.order_by(BlogPost.posted_at.desc()).paginate(page=page, per_page=per_page, error_out=False)

    for post in blog_posts.items:
        total_comments = db.session.query(func.count(BlogComment.id)).filter_by(blog_post_id=post.id).scalar()
        total_replies = db.session.query(func.count(BlogReply.id)).join(BlogComment).filter(BlogComment.blog_post_id == post.id).scalar()
        post.total_comments = total_comments + total_replies

    # Define a dictionary to map categories to CSS classes
    category_classes = {
        'Technology': 'tag-blue',
        'Science': 'tag-green',
        'Art': 'tag-orange',
        'Literature': 'tag-purple',
        'History': 'tag-brown',
        'Music': 'tag-pink',
        'Travel': 'tag-yellow',
        'Food': 'tag-red',
        'Sports': 'tag-teal',
        'Health': 'tag-lime',
        'custom': 'tag-custom',
        'default': 'tag-default'
    }

    # Pass the retrieved blog posts and category classes to the template
    return render_template('Navbar/blog.html', blog_posts=blog_posts,user=user, category_classes=category_classes)









    
    
# Your existing route for the contact page
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    user = get_current_user()

    if request.method == 'POST':
        if user is None:
            flash('You do not have permission to submit the contact form. Please log in first.', 'error')
        else:
            name = request.form['name']
            user_email = user.email  # Get the user's email directly from the 'user' object
            subject = request.form['subject']
            message = request.form['message']
            teacher_mentioned_id = request.form.get('teacher_mentioned_id')

            new_contact = Contact(
                user_id=user.id,
                teacher_mentioned_id=teacher_mentioned_id,
                name=name,
                user_email=user_email,  # Store the user's email
                subject=subject,
                message=message
            )

            db.session.add(new_contact)
            db.session.commit()

            flash('Your message has been submitted successfully.', 'success')

        return redirect(url_for('contact'))

    if user is None:
        flash('You do not have permission to access the contact page. Please log in first.', 'error')
        return redirect(url_for('login'))

    teachers = users.query.filter_by(role='teacher').all()

    # Pass the 'user' to the template
    return render_template('Navbar/contact.html', teachers=teachers, user=user)





@app.route('/htmlcourse')
def htmlcourse():
    user = get_current_user()
    if user is None:
        flash('You do not have permission to access HTML course page. Please log in first.', 'error')
        return redirect(url_for('login'))
    
    # Query the database to get all videos with the "htmlcourse" category
    videos = Video.query.filter_by(category='htmlcourse').all()
    return render_template('Courses/htmlcourse.html', videos=videos)

@app.route('/photography')
def photography():
    user = get_current_user()
    if user is None:
        flash('You do not have permission to access HTML course page. Please log in first.', 'error')
        return redirect(url_for('login'))
    
    # Query the database to get all videos with the "Photography" category
    videos = Video.query.filter_by(category='photography').all()
    
   
    return render_template('Courses/photography.html', videos=videos)

@app.route('/driving')
def driving():
    user = get_current_user()
    if user is None:
        flash('You do not have permission to access HTML course page. Please log in first.', 'error')
        return redirect(url_for('login'))
    
    # Query the database to get all videos with the "driving" category
    videos = Video.query.filter_by(category='driving').all()
    
   
    return render_template('Courses/driving.html', videos=videos)


@app.route('/writing')
def writing():
    user = get_current_user()
    if user is None:
        flash('You do not have permission to access HTML course page. Please log in first.', 'error')
        return redirect(url_for('login'))
    
    # Query the database to get all videos with the "writing" category
    videos = Video.query.filter_by(category='writing').all()
    
   
    return render_template('Courses/writing.html', videos=videos)

@app.route('/speaking')
def speaking():
    user = get_current_user()
    if user is None:
        flash('You do not have permission to access HTML course page. Please log in first.', 'error')
        return redirect(url_for('login'))
    
    # Query the database to get all videos with the "speaking" category
    videos = Video.query.filter_by(category='speaking').all()
    
   
    return render_template('Courses/speaking.html', videos=videos)


@app.route('/other')
def other():
    user = get_current_user()
    if user is None:
        flash('You do not have permission to access HTML course page. Please log in first.', 'error')
        return redirect(url_for('login'))
    
    # Query the database to get all videos with the "other" category
    videos = Video.query.filter_by(category='other').all()
    
   
    return render_template('Courses/other.html', videos=videos)





@app.route('/csscourse')
def csscourse():
    
    user = get_current_user()
    if user is None:
        flash('You do not have permission to access Csscourse page.Login first', 'error')
        return redirect(url_for('login'))
    # Query the database to get all videos with the "csscourse" category
    videos = Video.query.filter_by(category='css').all()
    return render_template('Courses/csscourse.html', videos=videos)

@app.route('/bootstrapcourse')
def bootstrapcourse():
    user = get_current_user()
    if user is None:
        flash('You do not have permission to access BootstrapCourse page.Login first', 'error')
        return redirect(url_for('login'))
    videos = Video.query.filter_by(category='bootstrap').all()
    return render_template('Courses/bootstrapcourse.html', videos=videos)

@app.route('/javascriptcourse')
def javascriptcourse():
    user = get_current_user()
    if user is None:
        flash('You do not have permission to access JavaScriptCourse page.Login first', 'error')
        return redirect(url_for('login'))
      # Query the database to get all videos with the "csscourse" category
    videos = Video.query.filter_by(category='javascript').all()
    return render_template('Courses/javascriptcourse.html', videos=videos)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login_input = request.form['login_input']  # Use 'login_input' field
        password = request.form['password']

        # Query the database for the user
        user = users.query.filter(
            (users.username == login_input) | (users.email == login_input),
            users.password == password).first()

        if user:
            session['user_id'] = user.id  # Store the user's ID in the session
            session['username'] = user.username  # Store the username
           

            if user.role == 'teacher':
                session['role'] = 'teacher'  
                # Redirect to the teacher dashboard
                return redirect(url_for('teacher_dashboard'))
            elif user.role == 'admin':
                session['role'] = 'admin'
                # Redirect to the admin dashboard
                return redirect(url_for('admin_dashboard'))
            else:
                # Redirect to the user interface or any other desired page
                return redirect(url_for('about'))  # Adjust to your page

        else:
            flash('Invalid username or password. Please try again.', 'error')

    return render_template('Navbar/login.html')

    

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        confirm_password = request.form.get('confirm_password')  # Get the 'confirm_password' field

        # Check if username or email already exists
        if users.query.filter_by(username=username).first() or users.query.filter_by(email=email).first():
            flash('Username or email already taken. Please choose different credentials.', 'danger')
        elif password != confirm_password:  # Check if passwords match
            flash('Passwords do not match. Please try again.', 'danger')
        else:
            # Add the new user to the database with the default 'user' role
            new_user = users(username=username, password=password, email=email, role='user')
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful. You can now login.', 'success')
            return redirect(url_for('login'))
    return render_template('Navbar/login.html')

@app.route('/admin_dashboard')
def admin_dashboard():
    # Check if the user is logged in
    user = get_current_user()
    if user is None:
        return redirect(url_for('login'))

    # Check if the user has the 'admin' role
    if user.role != 'admin':
        flash('You do not have permission to access the admin dashboard.', 'error')
        return redirect(url_for('about'))  # Redirect to a different page if not an admin

    return render_template('Dashboards/admin_dashboard.html')

@app.route('/teacher_dashboard')
def teacher_dashboard():
    # Check if the user is logged in
    user = get_current_user()
    if user is None:
        return redirect(url_for('login'))

    # Check if the user has the 'teacher' or 'admin' role
    if user.role not in ['teacher', 'admin']:
        flash('You do not have permission to access the teacher dashboard.', 'error')
        return redirect(url_for('about'))  # Redirect to a different page if not a teacher or admin

    return render_template('Dashboards/teacher_dashboard.html', user=user)
 # Pass the 'user' variable to the template


# Add a new route to display contact messages
@app.route('/teacher_messages/<int:teacher_id>')
def teacher_messages(teacher_id):
    # Check if the user is logged in
    user = get_current_user()
    if user is None:
        return redirect(url_for('login'))

    # Check if the user has the 'teacher' role
    if user.role != 'teacher':
        flash('You do not have permission to access the messages page.', 'error')
        return redirect(url_for('about'))  # Redirect to a different page if not a teacher

    # Retrieve contact messages where the teacher is mentioned
    contact_messages = Contact.query.filter_by(teacher_mentioned_id=teacher_id).all()

    return render_template('messages.html', user=user, contact_messages=contact_messages)

@app.route('/view_message/<int:message_id>')
def view_message(message_id):
    # Retrieve the message based on the message_id
    message = Contact.query.get(message_id)
    if message is None:
        flash('Message not found', 'error')
        return redirect(url_for('teacher_dashboard'))

    return render_template('view_message.html', message=message)




thumbnail_counter = 0
cover_pic_counter = 0
attachment_counter = 0

from flask import jsonify

@app.route('/create_post', methods=['GET', 'POST'])
def create_post():
    global thumbnail_counter, cover_pic_counter, attachment_counter
    # Fetch courses and courses categories from the database
    courses = Course.query.all()
    categories = [course.name for course in courses]
    
    if request.method == 'POST':
        # Extract form data
        title = request.form['title']
        author = request.form['author']
        thumbnail = request.files['thumbnail']
        cover_pic = request.files['cover_pic']
        content = request.form['content']
        blog_category = request.form['category']
        custom_category = request.form.get('customCategory')
        keywords = request.form['keywords']

        # Split keywords by commas and remove leading/trailing whitespaces
        keyword_list = [kw.strip() for kw in keywords.split(',')]

        is_featured = 'is_featured' in request.form
        status = request.form['status']

        # Check if the uploaded files have allowed extensions
        if (
            thumbnail and allowed_file(thumbnail.filename) and
            cover_pic and allowed_file(cover_pic.filename)
        ):
            # Increment counters
            thumbnail_counter += 1
            cover_pic_counter += 1

            # Generate filenames
            thumbnail_filename = f"blog_thumbnail_{thumbnail_counter}{os.path.splitext(thumbnail.filename)[1]}"
            cover_pic_filename = f"cover_pic_{cover_pic_counter}{os.path.splitext(cover_pic.filename)[1]}"

            # Save the files to the upload folders with the generated filenames
            thumbnail_path = os.path.join(app.config['UPLOAD_FOLDER_THUMBNAIL'], secure_filename(thumbnail_filename))
            cover_pic_path = os.path.join(app.config['UPLOAD_FOLDER_IMAGES'], secure_filename(cover_pic_filename))

            thumbnail.save(thumbnail_path)
            cover_pic.save(cover_pic_path)

            # Process multiple attachments
            attachments = request.files.getlist('attachments[]')
            attachment_filenames = []

            for attachment in attachments:
                if attachment and allowed_file(attachment.filename):
                    # Increment attachment counter
                    attachment_counter += 1

                    # Generate filename for attachment
                    attachment_filename = f"attachment_{attachment_counter}{os.path.splitext(attachment.filename)[1]}"
                    attachment_path = os.path.join(app.config['UPLOAD_FOLDER_ATTACHMENTS'], secure_filename(attachment_filename))

                    # Create the directory if it doesn't exist
                    os.makedirs(os.path.dirname(attachment_path), exist_ok=True)

                    attachment.save(attachment_path)
                    attachment_filenames.append(attachment_filename)

            # Concatenate attachment filenames with commas
            attachments_str = ','.join(attachment_filenames)

            # Get the UUID of the current user
            user_uuid = get_current_user().uuid

            # Create a new blog post with the user's UUID and timestamps
            new_post = BlogPost(
                title=title,
                author=author,
                thumbnail_filename=thumbnail_filename,
                cover_pic_filename=cover_pic_filename,
                attachments_filename=attachments_str,  # Save concatenated filenames
                content=content,
                blog_category=blog_category,
                custom_category=custom_category,
                keywords=keywords,
                is_featured=is_featured,
                status=status,
                posted_at=datetime.utcnow(),
                user_uuid=user_uuid,
            )

            # Add the post to the database
            db.session.add(new_post)
            db.session.commit()

            # Assuming you want to redirect to the blog page after creating the post
            return redirect(url_for('blog'))

    return render_template('Dashboards/create_blog.html', categories=categories)





# Function to generate thumbnail filename
def generate_thumbnail_filename(counter, file_extension):
    return f"blog_thumbnail_{counter}{file_extension}"

# Function to generate cover picture filename
def generate_cover_pic_filename(counter, file_extension):
    return f"blog_cover_pic_{counter}{file_extension}"




@app.route('/delete_blog/<int:blog_id>', methods=['POST'])
def delete_blog(blog_id):
    # Check if the user is logged in
    current_user = get_current_user()
    if current_user is None:
        flash('You need to be logged in to delete a blog post.', 'error')
        return redirect(url_for('login'))  # Redirect to login page if not logged in

    # Query the blog post to be deleted
    blog_post = BlogPost.query.get(blog_id)

    # Check if the logged-in user is the creator of the blog post
    if blog_post.user != current_user:
        flash('You do not have permission to delete this blog post.', 'error')
        return redirect(url_for('blog'))

    # Delete associated comments and replies
    comments = BlogComment.query.filter_by(blog_post_id=blog_id).all()
    for comment in comments:
        # Delete associated replies
        BlogReply.query.filter_by(comment_id=comment.id).delete()
        # Delete the comment itself
        db.session.delete(comment)

    # Delete associated files (thumbnail, cover pic, attachments)
    thumbnail_path = os.path.join(app.config['UPLOAD_FOLDER_THUMBNAIL'], blog_post.thumbnail_filename)
    cover_pic_path = os.path.join(app.config['UPLOAD_FOLDER_IMAGES'], blog_post.cover_pic_filename)

    # Delete thumbnail file
    if os.path.exists(thumbnail_path):
        os.remove(thumbnail_path)

    # Delete cover pic file
    if os.path.exists(cover_pic_path):
        os.remove(cover_pic_path)

    # Delete attachment files
    attachments = blog_post.attachments_filename.split(',')
    for attachment in attachments:
        attachment_path = os.path.join(app.config['UPLOAD_FOLDER_ATTACHMENTS'], attachment.strip())
        if os.path.exists(attachment_path):
            os.remove(attachment_path)

    # Delete the blog post itself
    db.session.delete(blog_post)

    # Commit changes to the database
    db.session.commit()

    flash('Blog post deleted successfully.', 'success')
    return jsonify({'redirect_url': url_for('blog')})


# Route for the teacher's admin video page
@app.route('/admin_video')
def admin_video():
    # Check if the user is logged in
    user = get_current_user()
    if user is None:
        return redirect(url_for('login'))

    # Check if the user has the 'teacher' role
    if user.role not in ['teacher', 'admin']:
        flash('You do not have permission to access Admin_video.', 'error')
        return redirect(url_for('login'))  # Redirect to a different page if not a teacher

    # Retrieve categories and their creators
    categories = Course.query.with_entities(Course.category, Course.creator_id).distinct().all()

    # Render the teacher's admin video page
    return render_template('Dashboards/admin_video.html', user=user, categories=categories)








@app.route('/upload_video', methods=['POST'])
def upload_video():
    # Check if the post request has the file parts for both video and thumbnail
    if 'video' not in request.files or 'thumbnail' not in request.files:
        return redirect(request.url)

    video_file = request.files['video']
    thumbnail_file = request.files['thumbnail']

    # If the user does not select a video file or a thumbnail file, return an error
    if video_file.filename == '' or thumbnail_file.filename == '':
        return "Both video and thumbnail files are required."

    # Check if the video file has an allowed extension
    if video_file and allowed_file(video_file.filename):
        # Get the category from the form
        category = request.form['category']

        # Generate a unique filename for the video based on the category and counter
        counter = 1
        while os.path.exists(os.path.join(app.config['UPLOAD_FOLDER_VIDEO'], generate_filename(category, counter, video_file.filename))):
            counter += 1

        video_filename = generate_filename(category, counter, secure_filename(video_file.filename))
        video_file.save(os.path.join(app.config['UPLOAD_FOLDER_VIDEO'], video_filename))

        # Generate a unique filename for the thumbnail based on the category and counter
        counter = 1
        while os.path.exists(os.path.join(app.config['UPLOAD_FOLDER_THUMBNAIL'], generate_video_thumbnail_filename(category, counter, thumbnail_file.filename))):
            counter += 1

        thumbnail_filename = generate_video_thumbnail_filename(category, counter, secure_filename(thumbnail_file.filename))
        thumbnail_file.save(os.path.join(app.config['UPLOAD_FOLDER_THUMBNAIL'], thumbnail_filename))

        # Get the current user
        user = get_current_user()

        if user:
            # Create a new Video record in the database with the video and thumbnail information
            title = request.form['title']
            description = request.form['description']
            user_id = user.id
            video_path = video_filename

            # Save the generated thumbnail filename in the video_thumbnail column
            video_thumbnail = thumbnail_filename

            # Set the upload_time to the current datetime
            upload_time = datetime.utcnow()  # You may need to import datetime

            new_video = Video(
                title=title,
                description=description,
                category=category,
                user_id=user_id,
                file_path=video_path,
                video_thumbnail=video_thumbnail,
                upload_time=upload_time
            )

            db.session.add(new_video)
            db.session.commit()

            # Redirect to a success page or display a success message
            return "Video and thumbnail uploaded successfully!"
            
        else:
            return "You must be logged in to upload a video."

    else:
        # The uploaded video file has an invalid extension
        return "Invalid video file format. Please upload a valid video file."


    

    # Function to generate a new filename
def generate_filename(category, counter, original_filename):
    # Get the file extension (e.g., '.mp4')
    file_extension = os.path.splitext(original_filename)[-1]
    new_filename = f"{category}_video_{counter}{file_extension}"
    return new_filename

def generate_video_thumbnail_filename(category, counter, original_filename):
    file_extension = os.path.splitext(original_filename)[-1]
    new_filename = f"{category}_video_thumbnail_{counter}{file_extension}"
    return new_filename




@app.route('/play_video/<int:video_id>', methods=['GET'])
def play_video(video_id):
    video = Video.query.get(video_id)

    if video:
        # Increment the view count
        video.views += 1
        db.session.commit()

        # Fetch suggested videos (videos from the same category excluding the current one)
        suggested_videos = Video.query.filter(
            Video.category == video.category,
            Video.id != video_id
        ).limit(3).all()

        # Render the video playback template with suggested videos
        return render_template('play_video.html', video=video, suggested_videos=suggested_videos)
    else:
        # Handle the case when the video is not found
        return "Video not found."
    







    
def time_ago(upload_time):
    now = datetime.utcnow()
    diff = now - upload_time
    days, seconds = diff.days, diff.seconds
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    if days > 0:
        return f"{days} day{'s' if days > 1 else ''} ago"
    elif hours > 0:
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    elif minutes > 0:
        return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
    else:
        return f"{seconds} second{'s' if seconds > 1 else ''} ago"
    
app.jinja_env.filters['timedelta'] = time_ago






@app.route('/admin/edit_user/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
     # Check if the user is logged in
    user = get_current_user()
    if user is None:
        return redirect(url_for('login'))

    # Check if the user has the 'admin' role
    if user.role != 'admin':
        flash('You do not have permission to access the admin dashboard.', 'error')
        return redirect(url_for('login'))  # Redirect to a different page if not an admin
    user = users.query.get_or_404(user_id)

    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        role = request.form['role']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password == confirm_password:
            user.username = username
            user.email = email
            user.role = role

            # Check if a new password was provided and update it
            if password:
                user.password = password  

            db.session.commit()

            flash('User details updated successfully.', 'success')
            return redirect(url_for('admin_users'))
        else:
            flash('Password and confirm password do not match.', 'error')

    return render_template('Dashboards/edit_user.html', user=user)




@app.route('/admin/deactivate_user/<int:user_id>', methods=['GET', 'POST'])
def deactivate_user(user_id):
     # Check if the user is logged in
    user = get_current_user()
    if user is None:
        return redirect(url_for('login'))

    # Check if the user has the 'admin' role
    if user.role != 'admin':
        flash('You do not have permission to access the admin dashboard.', 'error')
        return redirect(url_for('login'))  # Redirect to a different page if not an admin
    # Retrieve the user with the given user_id from the database
    user = users.query.get_or_404(user_id)

    if request.method == 'POST':
        # Check the user's status and toggle it
        if user.status == 'active':
            user.status = 'deactive'
            user.deactivated_at = datetime.now()  # Save the deactivation time
            flash('User account deactivated successfully.', 'success')
        else:
            user.status = 'active'
            flash('User account activated successfully.', 'success')

        db.session.commit()

        # Redirect back to the user management page
        return redirect(url_for('admin_users'))

    # Calculate the time difference
    time_difference = datetime.now() - user.deactivated_at if user.deactivated_at else None

    # Pass the current time to the template
    current_time = datetime.now()

    return render_template('Dashboards/deactivate_user.html', user=user, time_difference=time_difference, current_time=current_time)


@app.route('/delete_user/<int:user_id>', methods=['GET', 'POST'])
def delete_user(user_id):
   user_to_delete = users.query.get(user_id)
   if user_to_delete:
        
        
        db.session.delete(user_to_delete)
        db.session.commit()
        flash('user deleted successfully', 'success')
   else:
        flash('user not found', 'error')
    
   return redirect(url_for('admin_users'))








@app.route('/admin/update_user/<int:user_id>', methods=['POST'])
def update_user(user_id):
     # Check if the user is logged in
    user = get_current_user()
    if user is None:
        return redirect(url_for('login'))

    # Check if the user has the 'admin' role
    if user.role != 'admin':
        flash('You do not have permission to access the admin dashboard.', 'error')
        return redirect(url_for('login'))  # Redirect to a different page if not an admin
    # Retrieve the user with the given user_id from the database
    user = users.query.get_or_404(user_id)

    if request.method == 'POST':
        # Update user details and role based on form submission
        username = request.form['username']
        email = request.form['email']
        role = request.form['role']

        # Update the user's details and role in the database
        user.username = username
        user.email = email
        user.role = role
        db.session.commit()

        flash('User details updated successfully.', 'success')

        # Redirect back to the user management page
        return redirect(url_for('admin_users'))

    return render_template('Dashboards/edit_user.html', user=user)

# Route to handle the update user information form submission
@app.route('/update_user_info', methods=['POST'])
def update_user_info():
     # Check if the user is logged in
    user = get_current_user()
    if user is None:
        return redirect(url_for('login'))

    # Check if the user has the 'admin' role
    if user.role != 'admin':
        flash('You do not have permission to access the admin dashboard.', 'error')
        return redirect(url_for('login'))  # Redirect to a different page if not an admin
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    confirm_password = request.form['confirm_password']

    # Check if the passwords match
    if password != confirm_password:
        flash('Passwords do not match. Please try again.', 'error')
        return redirect(url_for('Dashboards/edit_user_info'))

    # Update the user's information in the session (we will implement this properly)
    session['username'] = username
    session['email'] = email

    flash('User information updated successfully.', 'success')
    return redirect(url_for('Dashboards/user_info'))

@app.route('/admin_users')
def admin_users():
    user = get_current_user()
    if user is None:
        return redirect(url_for('login'))

    # Check if the user has the 'admin' role
    if user.role != 'admin':
        flash('You do not have permission to access the admin dashboard.', 'error')
        return redirect(url_for('login'))  # Redirect to a different page if not an admin
    # Fetch and display the list of users from the database
   
    users_list = users.query.all()
    return render_template('Dashboards/admin_users.html', users_list=users_list)


# The logout route
@app.route('/logout')
def logout():
    if 'user_id' in session:
        session.pop('user_id')
        flash('You have been successfully logged out.', 'success')
    else:
        flash('You are not logged in.', 'info')
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)

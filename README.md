Flask Portfo Web App
Flask Portfo Web App is a dynamic microblogging platform designed to empower users with seamless communication and content sharing. This web application allows users to register, log in, and log out, create and share posts, engage with other users through comments, and personalize their profiles. With features such as password reset, followers, private messaging, and notes, Flask Portfo offers a comprehensive platform for users to interact and share their thoughts.

Key Features
User Authentication and Interaction
Register, Log In, and Log Out: Users can easily create accounts, log into the platform, and securely log out when done.
Password Reset: Forgot your password? No worries! Users can request a password reset for added convenience and security.
Content Creation and Engagement
Create and Share Posts: Once authenticated, users can share their thoughts, stories, and insights by creating posts.
Comments and Interactions: Engage with the community through comments, fostering discussions and feedback on posts.
Edit and Delete Posts: Users have full control over their content, with the ability to edit or remove posts as needed.
Personalized Profiles and Feeds
Profile Customization: Users can personalize their profiles with avatars and information about themselves.
Last Seen Status: Stay updated with the last seen status of other users for active engagement.
Following, Followed and Feed: Follow other users to view their posts separately and curate a personalized feed.

Additional Features
Notes and Organization: Users can jot down notes, organize them, and delete when necessary.
Limited Profile View: Gain insights into other users' profiles with limited information such as name, email, about, followers, and posts.

Technologies Used
Python: Backend development using the Flask framework.
SQLAlchemy: ORM operations for seamless database interactions.
Flask-Migrate: Database migrations made easy.
Flask-Bootstrap: Frontend styling for a responsive design.
Flask-CKEditor: Rich text editing for enhanced content creation.
Flask-Mail: Email notifications and support for password recovery.
Flask-Moment: Time formatting for a user-friendly experience.
JavaScript: Basic functionality for user notifications and user pop-ups.
Elasticsearch: Powerful search functionality for efficient content discovery.


Certainly! Here's an updated installation section in the README file, considering the config.py, .env, and .flaskenv files:

Flask Portfo Web App
Flask Portfo Web App is a dynamic microblogging platform designed to empower users with seamless communication and content sharing. This web application allows users to register, log in, and log out, create and share posts, engage with other users through comments, and personalize their profiles. With features such as password reset, followers, private messaging, and notes, Flask Portfo offers a comprehensive platform for users to interact and share their thoughts.

Key Features
User Authentication and Interaction
Register, Log In, and Log Out: Users can easily create accounts, log into the platform, and securely log out when done.
Password Reset: Forgot your password? No worries! Users can request a password reset for added convenience and security.
Content Creation and Engagement
Create and Share Posts: Once authenticated, users can share their thoughts, stories, and insights by creating posts.
Comments and Interactions: Engage with the community through comments, fostering discussions and feedback on posts.
Edit and Delete Posts: Users have full control over their content, with the ability to edit or remove posts as needed.
Personalized Profiles and Feeds
Profile Customization: Users can personalize their profiles with avatars and information about themselves.
Last Seen Status: Stay updated with the last seen status of other users for active engagement.
Following and Feed: Follow other users to view their posts separately and curate a personalized feed.
Additional Features
Notes and Organization: Users can jot down notes, organize them, and delete when necessary.
Limited Profile View: Gain insights into other users' profiles with limited information such as name, email, about, followers, and posts.
Technologies Used
Python: Backend development using the Flask framework.
SQLAlchemy: ORM operations for seamless database interactions.
Flask-Migrate: Database migrations made easy.
Flask-Bootstrap: Frontend styling for a responsive design.
Flask-CKEditor: Rich text editing for enhanced content creation.
Flask-Mail: Email notifications and support for password recovery.
Flask-Moment: Time formatting for a user-friendly experience.
JavaScript: Basic functionality for user notifications.
Elasticsearch: Powerful search functionality for efficient content discovery.
Installation
To run the Flask Portfo Web App locally, follow these steps:

Clone the repository:
git clone https://github.com/RalIlieva/flask-portfo-web-app.git

Navigate to the project directory:
cd flask-portfo-web-app

Create and activate a virtual environment (optional but recommended):
python3 -m venv venv
source venv/bin/activate

Install dependencies:
pip install -r requirements.txt

Set up the environment variables:
Create a .env file in the project root directory.
Add the following environment variables to the .env file:

SECRET_KEY=YourSecretKeyHere
DATABASE_URL=sqlite:///path/to/your/database.db
MAIL_SERVER=your_mail_server
MAIL_PORT=your_mail_port
MAIL_USE_TLS=1
MAIL_USE_SSL=False
MAIL_USERNAME=your_mail_username
MAIL_PASSWORD=your_mail_password
ELASTICSEARCH_URL=your_elasticsearch_url

Create a .flaskenv file in the project root directory:
FLASK_APP=run.py
FLASK_ENV=development

Run the database migrations:
flask db init
flask db migrate
flask db upgrade

Run the application:
flask run

Access the web app in your browser at http://localhost:5000.

Contributing
Contributions are welcome! If you'd like to contribute to Flask Portfo Web App, please follow these steps:

Fork the repository.
Create a new branch (git checkout -b feature/my-feature).
Make your changes.
Commit your changes (git commit -am 'Add new feature').
Push to the branch (git push origin feature/my-feature).
Create a new pull request.


License
This project is licensed under the MIT License - see the LICENSE file for details.
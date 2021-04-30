# education-for-all

## BTech Graduation final year project

***

## Structure

### analytics

##### - Token_API <http://localhost/api/analytics/ticket//>

##### - Log_API <http://localhost/api/analytics/log//>

### auth_prime

##### - User_Credential_API <http://localhost/api/user/cred//>

##### - User_Profile_API <http://localhost/api/user/prof//>

##### - Admin_Credential_API <http://localhost/api/admin/cred//>

##### - Admin_Privilege_API <http://localhost/api/admin/priv//>

##### - Images_API <http://localhost/api/user/image//>

### content_delivery

##### - Coordinator_API <http://localhost/api/content/coordinator//>

##### - Subject_API <http://localhost/api/content/subject//>

##### - Forum_API <http://localhost/api/content/forum//>

##### - Reply_API <http://localhost/api/content/reply//>

##### - Lecture_API <http://localhost/api/content/lecture//>

##### - Assignment_API <http://localhost/api/content/assignment//>

##### - Video_API <http://localhost/api/content/video//>

##### - Post_API <http://localhost/api/content/post//>

### cronjobs

##### - Telegram_BOT

##### - Log_Cleaner_BOT

### user_personal

##### - Submission_API <http://localhost/api/personal/submission///>

##### - Diary_API <http://localhost/api/personal/diary//>

##### - Enroll_API <http://localhost/api/personal/enroll//>

##### - Notification_API <http://localhost/api/personal/notification//>

***

### POSTMAN EXPORT FILE

##### <https://github.com/akash-sgta/education-for-all/blob/main/src/djangorestapi/static/docs/education-for-all.postman_collection.json>

***

### STEPS

    git clone https://github.com/akash-sgta/education-for-all.git
    
    cd education-for-all/src/djangorestapi

    linux only**
    apt install libmysqlclient-dev build-essential python3-dev gcc nginx

    python -m pip install -r requirements

    python manage.py makemigrations auth_prime analytics user_personal content_delivery

    python manage.py migrate --database=auth_db

    python manage.py createsuperuser --database=auth_db
    
    python manage.py migrate --database=app_db
    
    python manage.py check --deploy

#### Testing

    python manage.py runserver

#### Production

    python manage.py runserver 0.0.0.0:80

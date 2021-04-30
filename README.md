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

### System

```ubuntu 18.04 LTS```

### STEPS

```
git clone https://github.com/akash-sgta/education-for-all.git

cd education-for-all/src/djangorestapi

linux only**
apt install python3 python3-pip python3-dev libmysqlclient-dev build-essential gcc nginx

python -m pip install -r requirements

python manage.py makemigrations auth_prime analytics user_personal content_delivery

python manage.py migrate --database=auth_db

python manage.py createsuperuser --database=auth_db

python manage.py migrate --database=app_db

python manage.py check --deploy

python manage.py runserver
```

### Intermediate

```
ln -s /home/<user>/repositories/education-for-all/src/djangorestapi/config/<production or development>/djangorestapi_uwsgi_aws.ini /home/<user>/uwsgi.ini

ln -s /home/<user>/repositories/education-for-all/src/djangorestapi/manage.py /home/<user>/manage.py
```

#### Nginx

```
---------------nginx------------------

sudo nano /etc/nginx/conf.d/djangoproj.conf

>> paste all from respective *.conf in /config <<

sudo /etc/init.d/nginx start

sudo /etc/init.d/nginx restart

sudo /etc/init.d/nginx stop
```
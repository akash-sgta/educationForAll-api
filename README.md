# education-for-all

## BTech Graduation final year project

***

## Structure

```
base_api
    │
    ├ analytics
    │    ├ Token
    │    └ Log
    │
    ├ auth_prime
    │    ├ User_Credential
    │    ├ User_Profile
    │    ├ Admin_Credential
    │    ├ Admin_Privilege
    │    └ Image
    │
    ├ content_delivery
    │    ├ Coordinator
    │    ├ Subject
    │    ├ Forum
    │    ├ Reply <nested>
    │    ├ Lecture
    │    ├ Assignment
    │    ├ Video
    │    └ Post
    │
    ├ cronjobs
    │    ├ Notification*
    │    └ Token_Cleaner*
    │
    └ user_personal
        ├ Submission
        ├ Diary
        ├ Enroll
        └ Notification
```

***

### POSTMAN EXPORT FILE

##### <https://github.com/akash-sgta/education-for-all/blob/main/src/djangorestapi/static/docs/education-for-all.postman_collection.json>

***

### System

```ubuntu 18.04 LTS```

***

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

***

### Intermediate

```
create symbolic links for ease of access

ln -s /home/<user>/repositories/education-for-all/src/djangorestapi/config/<production or development>/djangorestapi_uwsgi_aws.ini /home/<user>/uwsgi.ini

ln -s /home/<user>/repositories/education-for-all/src/djangorestapi/manage.py /home/<user>/manage.py
```

***

#### Nginx

```
sudo nano /etc/nginx/conf.d/djangoproj.conf

>> paste all from respective *.conf in /config <<

sudo /etc/init.d/nginx start

sudo /etc/init.d/nginx restart

sudo /etc/init.d/nginx stop
```
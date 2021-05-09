# education-for-all

## BTech Graduation final year project

***

## Structure

```
base_api
    │
    ├ analytics
    │    ├ Token  <analytics/ticket/>
    │    └ Log    <analytics/log/>
    │
    ├ auth_prime
    │    ├ User_Credential  <user/cred/>
    │    ├ User_Profile <user/prof/>
    │    ├ Admin_Credential <admin/cred/>  
    │    ├ Admin_Privilege  <admin/priv/>
    │    └ Image    <user/image/>
    │
    ├ content_delivery
    │    ├ Coordinator  <content/cordinator/>
    │    ├ Subject  <content/subject/>
    │    ├ Forum  <content/forum/>
    │    ├ Reply <nested>  <content/reply/>  <content/reply2reply/>
    │    ├ Lecture  <content/lecture/>
    │    ├ Assignment  <content/assignment/> <content/mark/>
    │    ├ Video  <content/video/>
    │    └ Post  <content/post/>
    │
    ├ cronjobs
    │    ├ Notification*
    │    └ Token_Cleaner*
    │
    └ user_personal
        ├ Submission  <personal/submission/>
        ├ Diary  <personal/diary/>
        ├ Enroll  <personal/enroll/>
        └ Notification  <personal/notification/>
```

***

### POSTMAN EXPORT FILE

##### <https://github.com/akash-sgta/education-for-all/blob/main/src/djangorestapi/static/docs/education-for-all.postman_collection.json>

***

### System

```
ubuntu 18.04 LTS
nginx 1.14.0
python 3.6.9
gcc 7.5.0
```

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

#### LOC 

```
find . -name '*.php' | xargs wc -l | tail -1
8797
```
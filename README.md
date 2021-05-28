# education-for-all

## BTech Graduation final year project

***

## Structure

```
base_api
    │
    ├ analytics
    │    ├ Token  <analytics/ticket/>
    │    └ Log*
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

##### <https://www.getpostman.com/collections/90fa56e39ac2fa25ec66>

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

**linux only**
```
apt install python3 python3-pip python3-dev libmysqlclient-dev build-essential gcc nginx
```

**universal**
```
git clone https://github.com/akash-sgta/education-for-all.git

cd education-for-all/src/djangorestapi

python -m pip install -r requirements.txt

python manage.py makemigrations auth_prime analytics user_personal content_delivery cronjobs

python manage.py migrate --database=auth_db
python manage.py migrate --database=app_db
python manage.py migrate --database=default

python manage.py createsuperuser --database=auth_db

python manage.py test
python manage.py runserver
```

**only if willing to test production readyness**
```
python manage.py check --deploy
```

***

FOR BETTER CODE VISIBILITY : __fabiospampinato.vscode-highlight__

***

### Intermediate

```
create symbolic links for ease of access

ln -s /{your_path}/uwsgi.ini /home/<user>/uwsgi.ini

ln -s /{your_path}/manage.py /home/<user>/manage.py
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

***

#### LOC 

```
find . -name '*.py' | xargs wc -l | tail -1
7549

find . -name '*.html' | xargs wc -l | tail -1
1046

find . -name '*.css' | xargs wc -l | tail -1
7165

find . -name '*.py' | xargs wc -l | tail -1
28220
```

***

#### Cronjob

```
sudo /etc/init.d/cron stop

sudo /etc/init.d/cron start

sudo /etc/init.d/cron restart

python manage.py crontab add

python manage.py crontab remove
```
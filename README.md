# education-for-all

## BTech Graduation final year project

***

__Structure__
```
base_api
    │
    ├ analytics
    │    ├ Token  <analytics/ticket/>
    │    └ Log*
    │
    ├ auth_prime
    │    ├ User_Credential  <auth/user/cred/>
    │    ├ User_Profile <auth/user/prof/>
    │    ├ Admin_Credential <auth/admin/cred/>  
    │    ├ Admin_Privilege  <auth/admin/priv/>
    │    └ Image    <auth/user/image/>
    │
    ├ content_delivery
    │    ├ Coordinator  <content/cordinator/>
    │    ├ Subject  <content/subject/>
    │    ├ Forum  <content/forum/>
    │    ├ Reply <nested>  <content/reply/>  <content/reply2reply/>
    │    ├ Lecture  <content/lecture/>
    │    ├ Assignment  <content/assignment/> <content/assignment_mark//>
    │    ├ AssignmentMCQ  <content/multi/> <content/multi_mark//>
    │    ├ Video  <content/video/>
    │    └ Post  <content/post/>
    │
    ├ cronjobs
    │    ├ Notification*
    │    └ Token_Cleaner*
    │
    └ user_personal
        ├ Submission  <personal/submission_normal//>
        ├ SubmissionMCQ    <personal/submission_multi//>
        ├ Diary  <personal/diary/>
        ├ Enroll  <personal/enroll/>
        └ Notification  <personal/notification/>
```

***

__POSTMAN EXPORT FILE__\
link : __<https://www.getpostman.com/collections/b90615eaf8db65f21004>__

***

__System__
```
ubuntu 18.04 LTS
nginx 1.14.0
python 3.6.9
gcc 7.5.0
```

***

### STEPS

__linux only__
```
apt install python3 python3-pip python3-dev libmysqlclient-dev build-essential gcc nginx
```

__universal__
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

__only if willing to test production readyness__
```
python manage.py check --deploy
```

***
__FOR BETTER CODE VISIBILITY__\
vs-code-extension : __fabiospampinato.vscode-highlight__

***

__Intermediate__
```
create symbolic links for ease of access

ln -s /{your_path}/uwsgi.ini /home/<user>/uwsgi.ini
ln -s /{your_path}/manage.py /home/<user>/manage.py
```

***

__Nginx__
```
sudo nano /etc/nginx/conf.d/djangoproj.conf

>> paste all from respective *.conf in /config <<

sudo /etc/init.d/nginx start
sudo /etc/init.d/nginx restart
sudo /etc/init.d/nginx stop
```

***

__LOC__
```
find . -name '*.py' | xargs wc -l | tail -1
9331

find . -name '*.html' | xargs wc -l | tail -1
1063

find . -name '*.css' | xargs wc -l | tail -1
7165
```

***

__Cronjob__
```
sudo /etc/init.d/cron stop
sudo /etc/init.d/cron start
sudo /etc/init.d/cron restart

python manage.py crontab add
python manage.py crontab remove
```

***

__for contributing developers__
```
{
    "python.formatting.provider": "black"
    "python.formatting.blackArgs": [
        "--line-length",
        "128"
    ],
}
```

***

__Certbot__
```
sudo add-apt-repository ppa:certbot/certbot
sudo apt-get update
sudo apt-get install python3-certbot-nginx
```
echo ""
echo "**********************************************************"
echo "********* Things to do before running setup.sh ***********"
echo "**********************************************************"
echo "*      [1] Get configuration file from ADMIN.            *"
echo "* [2] Setup previously assigned test databases (if any). *"
echo "**********************************************************"
echo "*  [?] Do you want complete the tasks above ? [yes/no]   *"
echo "**********************************************************"
echo "== >"
echo ""
read ans
opt="yes"
if [ $ans = $opt ]
then
    echo ""
    echo "**********************************************************"
    echo "*            [*] Do not interrupt process !!             *"
    echo "**********************************************************"
    echo ""
    sleep 2

    sudo apt install python3 python3-pip python3-dev libmysqlclient-dev build-essential gcc nginx git
    python3 -m pip install virtualenv
    python3 -m virtualenv ~/education-for-all/venv
    ~/education-for-all/venv/bin/python3 -m pip install -r ~/education-for-all/src/djangorestapi/requirements.txt
    ~/education-for-all/venv/bin/python3 ~/education-for-all/src/djangorestapi/manage.py makemigrations auth_prime analytics user_personal content_delivery cronjobs
    ~/education-for-all/venv/bin/python3 ~/education-for-all/src/djangorestapi/manage.py migrate --database=auth_db
    ~/education-for-all/venv/bin/python3 ~/education-for-all/src/djangorestapi/manage.py migrate --database=app_db
    ~/education-for-all/venv/bin/python3 ~/education-for-all/src/djangorestapi/manage.py migrate --database=default
    sudo ln -s ~/education-for-all/src/djangorestapi/config/uwsgi.ini ~/uwsgi.ini
    sudo ln -s ~/education-for-all/src/djangorestapi/manage.py ~/manage.py
    ~/education-for-all/venv/bin/python3 ~/education-for-all/src/djangorestapi/manage.py crontab add

    echo ""
    echo "**********************************************************"
    echo "*      Do you want to create a superuser ? [yes/no]      *"
    echo "**********************************************************"
    echo "== > "
    echo ""
    read choice
    if [ $choice = $opt ]
    then
        ~/education-for-all/venv/bin/python3 ~/education-for-all/src/djangorestapi/manage.py createsuperuser --database=auth_db
    fi

    echo ""
    echo "**********************************************************"
    echo "*            Setting up nginx or apache server           *"
    echo "*              will have to be done manually             *"
    echo "*                        Thank you                       *"
    echo "**********************************************************"
    sleep 2
else
    echo ""
    echo "**********************************************************"
    echo "*                      See you soon                      *"
    echo "**********************************************************"
    echo ""
fi
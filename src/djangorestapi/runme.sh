sudo apt install python3 python3-pip python3-dev libmysqlclient-dev build-essential gcc nginx git
python3 -m pip install virtualenv

python3 -m virtualenv ../venv
source ../venv/bin/activate

python3 -m pip install -r requirements.txt
python3 manage.py makemigrations auth_prime analytics user_personal content_delivery cronjobs
python3 manage.py migrate --database=auth_db
python3 manage.py migrate --database=app_db
echo "Window will wait for 10s then ask for confirmation"
sleep 8
python3 manage.py createsuperuser --database=auth_db

# Creating symbolic links
ln -s config/uwsgi.ini ~/uwsgi.ini
ln -s manage.py ~/manage.py

echo "Setting up nginx or apache server will have to be done manually"
sleep 2
echo "Thank You"
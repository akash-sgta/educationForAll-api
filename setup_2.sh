~/education-for-all/venv/bin/python3 ~/education-for-all/src/djangorestapi/manage.py makemigrations auth_prime analytics user_personal content_delivery cronjobs
~/education-for-all/venv/bin/python3 ~/education-for-all/src/djangorestapi/manage.py migrate --database=auth_db
~/education-for-all/venv/bin/python3 ~/education-for-all/src/djangorestapi/manage.py migrate --database=app_db
echo "\n"
echo "Do you want to automatically create a superuser ? [y/n]"
read ans
opt="y"
if [ $ans = $opt ]
then
    ~/education-for-all/venv/bin/python3 ~/education-for-all/src/djangorestapi/manage.py createsuperuser --database=auth_db
else
    echo "All set. Only a few things are left to assemble."
fi

# Creating symbolic links
ln -s ~/education-for-all/src/djangorestapi/config/uwsgi.ini ~/uwsgi.ini
ln -s ~/education-for-all/src/djangorestapi/manage.py ~/manage.py

~/education-for-all/venv/bin/python3 ~/education-for-all/src/djangorestapi/manage.py crontab add
sudo /etc/init.d/cron start

echo "Setting up nginx or apache server will have to be done manually"
sleep 2
echo "Thank You"
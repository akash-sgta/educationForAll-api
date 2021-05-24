~/education-for-all/venv/bin/python3 ~/education-for-all/src/djangorestapi/manage.py makemigrations auth_prime analytics user_personal content_delivery cronjobs
~/education-for-all/venv/bin/python3 ~/education-for-all/src/djangorestapi/manage.py migrate --database=auth_db
~/education-for-all/venv/bin/python3 ~/education-for-all/src/djangorestapi/manage.py migrate --database=app_db
echo "\n"
echo "Do you want to automatically create a superuser ? [y/n]"
read -p ans
if [ "$ans" = "y" ]; then
    python3 manage.py createsuperuser --database=auth_db
else
    echo "All set. Only a few things are left to assemble."
fi

# Creating symbolic links
ln -s config/uwsgi.ini ~/uwsgi.ini
ln -s manage.py ~/manage.py

echo "Setting up nginx or apache server will have to be done manually"
sleep 2
echo "Thank You"
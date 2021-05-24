sudo apt install python3 python3-pip python3-dev libmysqlclient-dev build-essential gcc nginx git
python3 -m pip install virtualenv

python3 -m virtualenv venv
source venv/bin/activate

cd src/djangorestapi
python3 -m pip install -r requirements.txt

echo "\n"
echo "[--Things to do before running runme2.sh--]"
sleep 1
echo "[.] Setup the secter keys for all aspects"
sleep 1
echo "[.] Setup previously assigned databases (if any)"
sleep 1
echo "[.] Activate vevn if not activated"
sleep 1
echo "Thank You"
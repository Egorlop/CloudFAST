sudo apt update
sudo add-apt-repository ppa:deadsnakes/ppa -y

sudo apt-key adv --keyserver keyserver.ubuntu.com --recv E0C56BD4
echo "sudo deb http://repo.yandex.ru/clickhouse/deb/stable/ main/"
sudo apt update
sudo apt install -y clickhouse-server
sudo mv users.xml /etc/clickhouse-server/

sudo service clickhouse-server start
service clickhouse-server status
pip install -r requirements.txt
export HOST=localhost

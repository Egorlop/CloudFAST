sudo apt update
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt install python3.10
git clone https://github.com/Egorlop/CloudFAST

sudo apt-key adv --keyserver keyserver.ubuntu.com --recv E0C56BD4
echo "sudo deb http://repo.yandex.ru/clickhouse/deb/stable/ main/"
sudo apt update
sudo apt install -y clickhouse-server clickhouse-client

sudo service clickhouse-server start
service clickhouse-server status
##замена в xml
bash -c "cd CloudFAST && pip install -r requirements.txt"
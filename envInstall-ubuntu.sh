sudo apt install -y npm
sudo npm install -g n
sudo n stable
sudo apt install -y mongodb
service mongodb start
sudo apt install -y screen
sudo apt install -y python-pip
sudo pip install setuptools
sudo pip install pymongo
sudo pip install IPy
sudo apt install -y zmap
sudo pip install chardet

#假如sudo apt-get install npm 装不上npm，用以下命令
#curl -sL https://deb.nodesource.com/setup_10.x | sudo -E bash -
#sudo apt-get install -y nodejs

#假如sudo apt-get install mongodb装不上mongodb:
#首先需要导入 MongoDB 官方的 public key：
#sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 2930ADAE8CAF5059EE73BB4B58712A2291FA4AD5
#然后创建下载包的位置，根据所用的 Ubuntu 版本不同，略有区别：
#echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu xenial/mongodb-org/3.6 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-3.6.list
#sudo apt-get update
#sudo apt-get install -y mongodb-org
#sudo service mongod start
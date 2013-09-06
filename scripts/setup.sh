#!/bin/bash
#-----------------------
echo Installing packages
#-----------------------
# -f = fix broken packages
# -y = assume Y to prompts
sudo apt-get -f update
sudo apt-get -f -y install git
sudo apt-get -f -y install nginx
sudo apt-get -f -y install python-pip
#-----------------------
echo Setting up Python SDK for AWS
#-----------------------
sudo pip install --upgrade boto
#-----------------------
echo Getting code base from github and installing application
#-----------------------
cd /opt
sudo rm -rf OhHo4oop-ec2autoscale
sudo git clone https://github.com/miraculixx/OhHo4oop-ec2autoscale.git /opt/OhHo4oop-ec2autoscale
sudo ln -fs /opt/OhHo4oop-ec2autoscale ~/kooaba-worker
sudo ln -fs /opt/OhHo4oop-ec2autoscale /opt/kooaba-worker
sudo cp ~/kooaba-worker/scripts/init.d/kasworker /etc/init.d/kasworker
sudo update-rc.d kasworker defaults
#-----------------------
echo Setting up nginx
#-----------------------
cd /etc/nginx/sites-enabled
sudo ln -fs /opt/OhHo4oop-ec2autoscale/config/nginx-proxy-conf kooaba-worker
#-----------------------
echo Starting services
#-----------------------
sudo /etc/init.d/nginx restart
sudo /etc/init.d/kasworker restart
if [ "$1" == "autoscaler" ]
then
 sudo cp ~/kooaba-worker/scripts/init.d/autoscaler /etc/init.d/autoscaler
 sudo update-rc.d autoscaler defaults
 sudo /etc/init.d/autoscaler restart
fi
echo Done.
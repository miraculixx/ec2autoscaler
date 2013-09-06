Approach
--------
I first made sure I understood the specific task at hand. Then I set out to read up on AWS AutoScaling , Elastic Loadbalancer and CloudWatch, which I hadn't used before (I also didn't know too much about SNS, but that proofed fairly straight forward). 

Next I provisioned an EC2 instance manually (i.e. using the AWS console) to make sure I could run the provided worker/server script in the suggested setup with nginx. These steps are detailed below. 

Then I established the approach that I would take technology-wise. While the AWS user interfaces are easy to use, it becomes tedious to enter the same information over and over again. Also I found it errorprone to name resources in a consistent manner when done manually. Thus I started out using boto, the Python library for AWS, at first merely to automate the creation of new instances. With eating comes appetite, and I found more and more scenarios that could be automated (e.g. adding alarms, adding and removing instances to the load balancer, starting and stopping, retrieving summary information, etc.) . 

Similarly, with having to set up new instances not only based on the standard Ubuntu 12.04 server AMI, but also setting up the required software to run on top of it, I wanted an automated way to do this. Of course one obvious approach is to create a custom AMI with all software already installed, but that was a no-go according to the rules (or so I figured -- it might have been OK for this scenario, i.e. required for AutoScaling).

This is also a (major) reason I decided against the use of the AWS Autoscaling feature. Another reason is that Autoscaling (as I understand it) requires the launch of new instances, and the termination of these for every scale-out and scale-in, respectively. This didn't look promising when I started - with hindsight, this might have been a simpler, less time consuming approach. Other reasons included that I was interested to build an autoscaler myself (to learn what it entails), and I figured this was a good exercise. In the process I found [some shortcomings](wiki/Potential) of my approach which the Autoscaling feature would probably have solved out of the box. 

Self assessment
---------------
It is a pity that the system does not fully match the specification yet. Although the clientrun script, which executes the nine steps of the test scenario in sequence, demonstrates that the autoscaling works (out and in), the timings have not yet matched up. The reason is an inadequate set of alarms, combined with the delay of the 5-minute default statistics that CloudWatch provides. A test using 1-minute intervals (detailed monitoring) has not proven worthwile: this seems to generate additional load, causing the instances to overload faster (that's a guestimate based on a quick test).

Yet, all in all the autoscaler component, in concert with CloudWatch and SNS notifications, does what it is supposed to do. The admin utility is an extensible prototype implementation of a command line interface allowing further automation. There is some improvement [Potential](wiki/Potential)


Steps
-----
* Install Amazon AWS EC2 Tools

   This includes setting the respective AWS command line environments. 
   The AWS settings are in config/ec2rc, which can be sourced to setup the environment

* Install one manual instance for a test drive

   Found the Ubuntu 12.04 Server version using the Classic Wizard in AWS Management Console

   * type: m1.small
   * ami: Ubuntu 12.04 Server Edition 
   * Login 
```
ssh -i config/OhHo4oop.pem ubuntu@ec2-54-228-34-54.eu-west-1.compute.amazonaws.com
```

* Install nginx
There was a problem with the apt-get setup, which needed correction first. Then install nginx
```
sudo apt-get update
sudo apt-get install nginx
```

* Created simple client script using httperf

* Install git client to speed up deployment of code (pull principle)
```
sudo apt-get install git
```

* Create a simple [deployment script](https://github.com/miraculixx/OhHo4oop-ec2autoscale/blob/master/scripts/update.sh) based on git, and install a first version. With this approach, we can easily update the code on the servers by executing the update script (manually or automatically)
```
sudo git clone https://github.com/miraculixx/OhHo4oop-ec2autoscale.git /opt/OhHo4oop-ec2autoscale
/opt/OhHo4oop-ec2autoscale/scripts/update.sh
```

* Setup nginx proxy and start the worker server
```
# reconfigure nginx (one-time)
$ cd /etc/nginx/sites-enabled
$ sudo ln -fs /opt/OhHo4oop-ec2autoscale/config/nginx-proxy-conf kooaba-worker
$ sudo /etc/init.d/nginx reload
# start the server (every time server is restarted)
$ source /opt/OhHo4oop-ec2autoscale/scripts/setenv
$ /opt/OhHo4oop-ec2autoscale/scripts/startsrv.sh

Serving at http://localhost:30001 using 5 worker processes
To exit press Ctrl-C
[Process-1]	starting server
[Process-2]	starting server
[Process-3]	starting server
[MainProcess]	starting server
[Process-4]	starting server
```

* Run the client to see if it is basically working
```
$ scripts/clientrun.sh 
httperf --client=0/1 --server=ohho4oop-1996069.eu-west-1.elb.amazonaws.com --port=30000 --uri=/work --rate=1 --send-buffer=4096 --recv-buffer=16384 --num-conns=300 --num-calls=1
```
Output at server as follows. This demonstrates that the nginx proxy forwarding and processing in the workers is working as planned. The /work requests are from the client, the /ping requests are the health checks issued by the load balancer (2 per minute).
```
[Process-2]	"GET /ping HTTP/1.0" 200 -
[MainProcess]	"GET /ping HTTP/1.0" 200 -
[Process-4]	"GET /ping HTTP/1.0" 200 -
[Process-3]	w=36867	duration=0.580976963043
[Process-3]	"GET /work HTTP/1.0" 200 -
[MainProcess]	w=36867	duration=0.529134988785
[MainProcess]	"GET /work HTTP/1.0" 200 -
[Process-1]	w=36867	duration=0.452090978622
[Process-1]	"GET /work HTTP/1.0" 200 -
[Process-2]	w=36867	duration=0.531271934509
[Process-2]	"GET /work HTTP/1.0" 200 -
[Process-3]	w=36867	duration=0.524964094162
[Process-3]	"GET /work HTTP/1.0" 200 -
[Process-4]	w=36867	duration=0.508056879044
[Process-4]	"GET /work HTTP/1.0" 200 -
[Process-3]	w=36867	duration=0.474159002304
[Process-3]	"GET /work HTTP/1.0" 200 -
[Process-4]	"GET /ping HTTP/1.0" 200 -
```

* We have one instance working. Next obvious steps are 
  1. to create a new EC2 instance, 
  2. set it up exactly the same way as the base instance
  3. configure the AWS auto scaling

  The current setup of the EC2 instance was done manually, but obviously that is not a sustainable
  approach for a prouction environment. It takes too long to set up a new instance and it is error
  prone. So we will want to automate this.  

* To this end, wrote an [admin utility](https://github.com/miraculixx/OhHo4oop-ec2autoscale/blob/master/src/client/admin.py). With this, creating a new instance is a single command:
```
$ python src/client/admin.py -a 
Creating EC2 Connection
Creating instance
Created instance i-24be746e
```

* The details of the new instance are easily retrieved by another command:
```
$ python src/client/admin.py -l 
        id   key_name      state                                    public_dns_name
i-f28346b8   Iji4xohf    stopped                                                   
i-24be746e   OhHo4oop    pending    ec2-54-228-5-40.eu-west-1.compute.amazonaws.com
i-56726a1f       eval    running  ec2-54-247-160-17.eu-west-1.compute.amazonaws.com
i-76e92d3c   Iji4xohf    stopped                                                   
i-204b836a   OhHo4oop    running  ec2-54-228-37-115.eu-west-1.compute.amazonaws.com
i-fed413b4   Iji4xohf    stopped                                                   
i-75b1413d       eval    running  ec2-46-137-63-234.eu-west-1.compute.amazonaws.com
```

* Once the instance is in running state, it can be boot strapped (install all software required)
by the following command. This will automatically copy setup.sh and execute it. setup.sh issues the appropriate apt-get commands and gets our server's code from github. It also sets up the nginx proxy accordingly and restarts nginx.
```
$ scripts/bootstrap.sh  ec2-54-228-5-40.eu-west-1.compute.amazonaws.com
```
* We can also use an arbitrary machine to run the autoscaler (my own implementation) by giving the
autoscaler parameter. This will use /etc/init.d/autoscaler to start the autoscaler service.
```
$ scripts/bootstrap.sh  ec2-54-228-5-40.eu-west-1.compute.amazonaws.com autoscaler
```

* To see if services are running, the admin script provides a ping command:
```
$ scripts/admin.sh --ping -i i-204b836a
Worker-Ping at http://ec2-54-228-18-168.eu-west-1.compute.amazonaws.com:30000/ping
OK
Scaler-Ping at http://ec2-54-228-18-168.eu-west-1.compute.amazonaws.com:10000/ping
OK
```

* Further we can test the autoscaler by either running the scale up/down policies directly, or by using the alert mechanism of CloudWatch:
```
# select the first stopped instance and start it, register in load balancer
$ scripts/admin.sh --scale-up
# select the first non _base instance and stop it, de-register from load balancer
$ scripts/admin.sh --scale-down
```

* Retrieving a list of defined alarms in CloudWatch:
```
$ scripts/admin.sh --list-alarms
           type                                name                         metric period       dimension                   topic(short)
   loadbalancer                    HighRequestCount      RequestCount(Average)>2.0     60        Iji4xohf             autoscale-Iji4xohf
      autoscale                    KaseHighCPUAlarm  CPUUtilization(Average)>=35.0     60    asg-Beecae8U      policyName/sp-UP-Beecae8U
      autoscale                     KaseLowCPUAlarm  CPUUtilization(Average)<=35.0     60    asg-Beecae8U    policyName/sp-DOWN-Beecae8U
       instance         OhHo4oop:cpuhigh:i-1e06d154  CPUUtilization(Average)>=65.0    300      i-1e06d154             autoscale-OhHo4oop
       instance         OhHo4oop:cpuhigh:i-204b836a  CPUUtilization(Average)>=65.0    300      i-204b836a             autoscale-OhHo4oop
       instance          OhHo4oop:cpulow:i-1e06d154  CPUUtilization(Average)>=20.0    300      i-1e06d154             autoscale-OhHo4oop
       instance          OhHo4oop:cpulow:i-204b836a  CPUUtilization(Average)>=20.0    300      i-204b836a             autoscale-OhHo4oop
```

Client/Development server
-------------------------
* Install httperf
```
sudo apt-get install httperf
```

* Took the server for a test drive using httperf

  * The client 
```
httperf --server localhost --port $KAS_PORT --num-conn $KAS_NUMCONN --uri /work --period=1
```
This implements the client processing as described in the email, 
```
Each client will query the /work path on port 30000 (via the load balancer) and then 
wait one second before sending next query, i.e. it will generate roughly one third of 
the full CPU load.
```

  * The server output:
```
> python src/server/server.py
[Process-1]	starting server
[MainProcess]	starting server
[Process-2]	starting server
[Process-3]	starting server
[Process-4]	starting server
[Process-3]	"GET ping HTTP/1.1" 404 -
[Process-4]	"GET /ping HTTP/1.1" 200 -
[Process-4]	"GET /ping HTTP/1.1" 200 -
[MainProcess]	"GET /work HTTP/1.1" 200 -
[Process-3]	"GET /work HTTP/1.1" 200 -
[Process-2]	"GET /work HTTP/1.1" 200 -
[MainProcess]	"GET /work HTTP/1.1" 200 -
...
```

* Install Python AWS API (boto) and ssh for automating some tasks
```
sudo apt-get install python-pip
sudo pip install boto
sudo pip install ssh
```


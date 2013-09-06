Components
==========
The autoscaling system is built of the following major components:

* [kasworker](https://github.com/miraculixx/OhHo4oop-ec2autoscale/blob/master/src/server.py) - the server script (as provided, slight modifications, see [here](https://github.com/miraculixx/OhHo4oop-ec2autoscale/commits/master/src/server.py))
* [autoscaler](https://github.com/miraculixx/OhHo4oop-ec2autoscale/blob/master/src/scaler.py) - the autoscaler, processes notifications and decides to start or stop instances
* [admin](https://github.com/miraculixx/OhHo4oop-ec2autoscale/blob/master/src/admin.py) - a command line interface to simplify the use of EC2, CloudWatch, Elastic Loadbalancer, SNS, including several scripts (e.g. init.d, instance setup etc.) 
* nginx - used as a front proxy server to the python scripts  
* AWS, including EC2, CloudWatch, Elastic Loadbalancer (ELB) and Simple Notification Services (SNS)
* Other ubuntu-provided (apt-get) packages (python, httperf).

autoscaler and admin are written by me. The kasworker is the initial server.py provided with a fancy name, the other elements are third party software components.

The system works as follows:

![Overview Diagram](https://raw.github.com/miraculixx/OhHo4oop-ec2autoscale/master/doc/architecture.jpg)

1. the base instance (i-204b836a) runs the kasworker and autoscaler as separate python scripts. The kasworker is responsible to process the /ping and /work requests to port 30001. The autoscaler receives notifications from SNS through the POST method, and also provides a GET /ping URI on port 10001. Note that the autoscaler could technically run on a third, independent control node that does not run the kasworker.

2. Clients make requests to the load balancer on port 30000, which forwards the requests to the base instance. There nginx forwards the requests to localhost:30001, where the kasworker threads process requests. Similarly, SNS delivers notifications to port 10000 which nginx forwards to localhost:10001. 

3. An additional instance (i-1e06d154) is pre-configured to run the kasworker but is stopped at first. Both instances have alarms defined in CloudWatch. The alarms are configured such that an OK notification is sent to the autoscaler on reaching a lower cpu limit, and an ALARM message is sent on reaching an upper cpu limit. 

4. On receiving a cpu-high ALARM notification, the autoscaler starts the second instance and registers it with the load balancer. 

5. On receiving a cpu-low OK notification, the autoscaler stops the second instance and de-registers it from the load balancer. This is to avoid the ELB disregarding an instance that is not available most of the time (not sure this is true, but that's the behaviour I observed).

6. The admin component is used to interact with the various AWS products through the Python SDK provided by Amazon. This simplifies and automates the addition of new instances, provisioning of the software, adding and listing monitoring alarms, etc. The component is written so that its output can be processed by other scripts (e.g. awk) to automate further tasks.  

7. nginx serves as the front proxy to the python scripts. This avoids to having to deal with lower level socket issues.

8. CloudWatch is used for system monitoring and alert generation. SNS is used to deliver alerts to the autoscaler. EC2 instantiates and runs the virtual machines. ELB is used to distribute the load evenly accross the two instances. httperf is used as a simple means to generate load.

9. By design, the autoscaler can handle more than 1 additional node. It queries EC2 for available instances (filtered to "my" instances), and scales out or in as needed. At most one instance is started or stopped per CloudWatch notification. Repeated notifications will trigger further scaling action.
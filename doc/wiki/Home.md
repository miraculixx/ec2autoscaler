Welcome to the OhHo4oop-ec2autoscale wiki!

Contents
--------
* [Architecture](wiki/Architecture)
* [Steps taken](wiki/Overview)
* [Sample Run](wiki/Sample Run), [Sample Run 2](wiki/Sample Run 2)
* [Admin Utility](wiki/Admin utility)
* [System setup](wiki/System setup)
* [Improvement Potential](wiki/Potential)
* [Software and Documentation](wiki/References)

* [Reset to scaled-down state](wiki/Reset Scaled-Down)

Purpose
-------
This is a collection of python and bash scripts that fulfill the following test scenario:
 
>There will be four clients (A to D) querying your system. Each client will query the /work path on port >30000 (via the load balancer) and then wait one second before sending next query, i.e. it will generate >roughly one third of the full CPU load. There are multiple stages of the test, each takes at least 5 >minutes:
>
>1.   Client A starts requests. Single instance should handle these.
>2.  Client B starts requests. Single instance should handle these.
>3.  Client C starts requests. Second instance should be started to accommodate the load.
>4.  Client D starts requests.
>5.  Client D stops requests.
>6.  Client B stops requests. The second instance should be shut down.
>7.  No changes.
>8.  Client C stops requests.
>9.  Client A stops requests.


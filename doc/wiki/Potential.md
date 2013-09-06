* The autoscaler starts instances and adds them to the loader balancer without checking if this actually happend. As in AWS AutoScaling the (my) autoscaler should also have a long-running process to verify the health state of any instance, so it can take corrective actions.

* The current autoscaling policy is a direct reaction to the notifications received from CloudWatch, i.e. the autoscaler reacts whenever there is an event. A more sophisticated approach would take into account recent actions, e.g. so that a just started instance is not immediately shut down again, and vice versa.

* The processes currently all run as user root, which is inappropriate for security reasons in a production environment. 
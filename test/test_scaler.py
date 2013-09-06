# To change this template, choose Tools | Templates
# and open the template in the editor.

import unittest
import json
from scaler import *

class  Test_scalerTestCase(unittest.TestCase):
    #def setUp(self):
    #    self.foo = Test_scaler()
    #

    #def tearDown(self):
    #    self.foo.dispose()
    #    self.foo = None

    def test_process_msg(self):
        msg = {u'SignatureVersion': u'1', u'Timestamp': u'2013-02-03T16:54:54.591Z', u'Signature': u'veLg7a5pPGOgKvVgYX4ndW2eHqDCD0B0KKBb+yFfh7YzYrTHdYe3Fh0xMx3lQfIjTz/cu2mWU+GomwVV8Aa7GkB8JCRlFpx2HUjj0m8ll6stjOnnwS5Pj+LVx7d3kf/1pKtbO+Rmt4F4O8LWioisX40boS7qcSWGnbWTIh1Sxk4=', u'SigningCertURL': u'https://sns.eu-west-1.amazonaws.com/SimpleNotificationService-f3ecfb7224c7233fe7bb5f59f96de52f.pem', u'MessageId': u'58e92ee6-5939-5f8d-bba0-676ec1a714eb', u'Message': u'{"AlarmName":"OhHo4oop:cpuhigh:i-24be746e","AlarmDescription":"Automatic metric","AWSAccountId":"237471159969","NewStateValue":"OK","NewStateReason":"Test state","StateChangeTime":"2013-02-03T16:54:54.534+0000","Region":"EU - Ireland","OldStateValue":"INSUFFICIENT_DATA","Trigger":{"MetricName":"CPUUtilization","Namespace":"None","Statistic":"AVERAGE","Unit":"Percent","Dimensions":[{"name":"InstanceId","value":"i-24be746e"}],"Period":60,"EvaluationPeriods":1,"ComparisonOperator":"GreaterThanOrEqualToThreshold","Threshold":35.0}}', u'UnsubscribeURL': u'https://sns.eu-west-1.amazonaws.com/?Action=Unsubscribe&SubscriptionArn=arn:aws:sns:eu-west-1:237471159969:autoscale-OhHo4oop:afa96aa6-2cbc-4feb-87f0-1a330015be52', u'Type': u'Notification', u'TopicArn': u'arn:aws:sns:eu-west-1:237471159969:autoscale-OhHo4oop', u'Subject': u'OK: "OhHo4oop:cpuhigh:i-24be746e" in EU - Ireland'}
        body = json.loads(msg['Message'])
        name = body['AlarmName']
        state = body['NewStateValue']
        prev_state = body['OldStateValue']

    def test_scale_down_base(self):
        scaler = AutoScaler()
        scaler.scale_down('i-204b836a')

    def test_scale_down_specific(self):
        scaler = AutoScaler()
        scaler.scale_down('i-24be746e')

    def test_scale_down_any(self):
        scaler = AutoScaler()
        scaler.scale_down('*')

    def test_scale_up(self):
        scaler = AutoScaler()
        scaler.scale_up()

    def test_connect_lb(self):
        scaler = AutoScaler()
        elb = scaler.connect_elb()
        self.assertIsNotNone(elb, "elb should not be none")

    def test_process_notification_OK(self):
        scaler = AutoScaler()
        id = scaler.process_notification('OhHo4oop:reqcount:OhHo4oop', 'OK', 'ALARM')
        self.assertIsNotNone(id, "Expected an instance id")

    def test_process_notification_ALARM(self):
        scaler = AutoScaler()
        id = scaler.process_notification('OhHo4oop:reqcount:OhHo4oop', 'ALARM', 'OK')
        self.assertIsNotNone(id, "Expected an instance id")

if __name__ == '__main__':
    unittest.main()


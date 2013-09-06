#!/bin/bash
wget localhost:10001 --post-file=msg/notification_body --header="x-amz-sns-topic-arn: arn:aws:sns:us-east-1:123456789012:MyTopic" --header="x-amz-sns-message-type: Notification"

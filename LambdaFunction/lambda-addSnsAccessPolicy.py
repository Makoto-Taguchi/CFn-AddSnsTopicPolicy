import json
import boto3
import logging
import cfnresponse

logger = logging.getLogger()
logger.setLevel(logging.INFO)

sns = boto3.client('sns')

def lambda_handler(event, context):
  logger.info("event == {}".format(event))
  response = None

  topicArn = event['ResourceProperties']['TopicArn']
  awsAccountId = event['ResourceProperties']['AwsAccountId']

  addPolicy = {
    "Sid": "AWSEvent_Allow",
    "Effect": "Allow",
    "Principal": {
      "Service": "events.amazonaws.com"
    },
    "Action": "sns:Publish",
    "Resource": topicArn,
    "Condition": {
      "StringEquals": {
        "AWS:SourceAccount": awsAccountId
      }
    }
  }

  if event['RequestType'] == 'Create':
    # 既存のトピックポリシーを取得
    attributes = sns.get_topic_attributes(TopicArn = topicArn)
    policy = eval(attributes["Attributes"]["Policy"])
    logger.info("policy = {}".format(policy))

    # EventBridgeからのパブリッシュ許可を追記
    policy["Statement"].append(addPolicy)
    logger.info("updatepolicy = {}".format(policy))

    # トピックポリシーを上書き
    responce=sns.set_topic_attributes(
      TopicArn=topicArn,
      AttributeName='Policy',
      AttributeValue=json.dumps(policy)
    )

  if event['RequestType'] == 'Update':
    cfnresponse.send(event, context, cfnresponse.SUCCESS, {})

  if event['RequestType'] == 'Update':
    cfnresponse.send(event, context, cfnresponse.SUCCESS, {})

  logger.info("response == {}".format(responce))
  cfnresponse.send(event, context, cfnresponse.SUCCESS, responce)
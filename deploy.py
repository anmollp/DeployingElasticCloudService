#!/usr/bin/env python
# coding: utf-8

import sys
import os
from requests_aws4auth import AWS4Auth, AWS4SigningKey, StrictAWS4Auth 
import requests 
import xml.etree.ElementTree as ET
from print_http import print_request_and_response

avg_cpu_utilization = float(sys.argv[1])

access_key = os.environ.get("AWS_ACCESS_KEY_ID") 
secret_key = os.environ.get("AWS_SECRET_ACCESS_KEY") 
auth = AWS4Auth(access_key, secret_key, 'us-east-1', 'ec2') 

# using instance id from Homework 2.
i_id = 'i-0a0eb490ba1b5013c'

response_task_1 = requests.request("GET", 
                            url="http://ec2.us-east-1.amazonaws.com" 
                                "?Action=CreateImage" 
                                "&Version=2016-11-15" 
                                "&InstanceId={instance_id}" 
                                "&Name=Hw2Extension".format(instance_id=i_id), 
                                auth=auth) 

root = ET.fromstring(response_task_1.text)
image_id = None
if response_task_1.status_code == requests.codes.ok:
    image_id = root.find('{http://ec2.amazonaws.com/doc/2016-11-15/}imageId').text

print_request_and_response(response_task_1, "messages.txt")

my_vpc = 'vpc-08de330c45d57b992'
security_group_name = 'Hw2ExtensionSG'
response_task_2_1 = requests.request("GET",
                                    url="http://ec2.us-east-1.amazonaws.com/"
                                     "?Action=CreateSecurityGroup"
                                     "&Version=2016-11-15" 
                                     "&GroupName={sg_name}"
                                     "&GroupDescription=Hw2Swarm"
                                     "&VpcId={vpc_id}".format(vpc_id=my_vpc, sg_name=security_group_name),
                                    auth=auth)

print_request_and_response(response_task_2_1, "messages.txt")

root = ET.fromstring(response_task_2_1.text)
group_id = None
if response_task_2_1.status_code == requests.codes.ok:
    group_id = root.find('{http://ec2.amazonaws.com/doc/2016-11-15/}groupId').text

response_task_2_2 = requests.request("GET",
                                    url="http://ec2.us-east-1.amazonaws.com/"
                                     "?Action=AuthorizeSecurityGroupIngress"
                                     "&Version=2016-11-15"
                                     "&GroupId={gid}"
                                     "&IpPermissions.1.IpProtocol=tcp"
                                     "&IpPermissions.1.FromPort=8888"
                                     "&IpPermissions.1.ToPort=8888"
                                     "&IpPermissions.1.IpRanges.1.CidrIp=0.0.0.0/0"
                                     "&IpPermissions.2.IpProtocol=tcp"
                                     "&IpPermissions.2.FromPort=22"
                                     "&IpPermissions.2.ToPort=22"
                                     "&IpPermissions.2.IpRanges.1.CidrIp=0.0.0.0/0"
                                     "&IpPermissions.3.IpProtocol=tcp"
                                     "&IpPermissions.3.FromPort=80"
                                     "&IpPermissions.3.ToPort=80"
                                     "&IpPermissions.3.IpRanges.1.CidrIp=0.0.0.0/0".format(gid=group_id),
                                     auth=auth)

print_request_and_response(response_task_2_2, "messages.txt")

response_task_3 = requests.request("GET",
                                  url="http://ec2.us-east-1.amazonaws.com/"
                                   "?Action=CreateLaunchTemplate"
                                   "&Version=2016-11-15"
                                   "&LaunchTemplateName=Hw2Extension"
                                   "&VersionDescription=APIVersion"
                                   "&LaunchTemplateData.SecurityGroupId={gid}"
                                   "&LaunchTemplateData.ImageId={imageId}"
                                   "&LaunchTemplateData.KeyName={key}"
                                   "&LaunchTemplateData.InstanceType=t2.micro"
                                   "&LaunchTemplateData.Placement.AvailabilityZone={my_zone}".format(gid=group_id, 
                                                                                           imageId=image_id,
                                                                                           my_zone='us-east-1',
                                                                                                    key='eel6761'),
                                  auth=auth)

print_request_and_response(response_task_3, "messages.txt")

response_task_4_1 = requests.request("GET",
                                    url="http://ec2.us-east-1.amazonaws.com/"
                                    "?Action=DescribeSubnets"
                                    "&Version=2016-11-15",
                                    auth=auth)

print_request_and_response(response_task_4_1, "messages.txt")

root = ET.fromstring(response_task_4_1.text)
subnet_ids = []
subnet_set = None
if response_task_4_1.status_code == requests.codes.ok:
    subnet_set = root.find('{http://ec2.amazonaws.com/doc/2016-11-15/}subnetSet')
    for item in subnet_set:
        subnet_ids.append(item.find("{http://ec2.amazonaws.com/doc/2016-11-15/}subnetId").text)

auth2 = AWS4Auth(access_key, secret_key, 'us-east-1', 'elasticloadbalancing')
response_task_4_2 = requests.request("GET",
                                    url="http://elasticloadbalancing.us-east-1.amazonaws.com/"
                                     "?Action=CreateLoadBalancer"
                                     "&Name=Hw2ExtensionLoadBalancer"
                                     "&Version=2015-12-01"
                                     "&SecurityGroups.member.1={gid}"
                                     "&Subnets.member.1={sub0}"
                                     "&Subnets.member.2={sub1}".format(sub0=subnet_ids[0], sub1=subnet_ids[1], gid=group_id),
                                     auth=auth2)

print_request_and_response(response_task_4_2, "messages.txt")

root = ET.fromstring(response_task_4_2.text)
load_balancer_urls = []
load_balancer_arns = []
if response_task_4_2.status_code == requests.codes.ok:
    urls = root.findall('.//{http://elasticloadbalancing.amazonaws.com/doc/2015-12-01/}DNSName')
    arns = root.findall('.//{http://elasticloadbalancing.amazonaws.com/doc/2015-12-01/}LoadBalancerArn')
    for load_balancer_url, load_balancer_arn in zip(urls, arns):
        load_balancer_urls.append(load_balancer_url.text)
        load_balancer_arns.append(load_balancer_arn.text)

response_task_5_1 = requests.request("GET",
                                    url="http://ec2.us-east-1.amazonaws.com/"
                                     "?Action=DescribeVpcs"
                                     "&Version=2016-11-15", 
                                    auth=auth)
print_request_and_response(response_task_5_1, "messages.txt")

root = ET.fromstring(response_task_5_1.text)
vpc_ids = []
vpc_set = None
if response_task_5_1.status_code == requests.codes.ok:
    vpc_set = root.find('{http://ec2.amazonaws.com/doc/2016-11-15/}vpcSet')
    for item in vpc_set:
        vpc_ids.append(item.find("{http://ec2.amazonaws.com/doc/2016-11-15/}vpcId").text)

# Here assuming the first created vpc is being used.
response_task_5_2 = requests.request("GET",
                                  url="http://elasticloadbalancing.amazonaws.com/"
                                   "?Action=CreateTargetGroup"
                                   "&Name=Hw2Extension-targets"
                                   "&HealthyThresholdCount=5"
                                   "&UnhealthyThresholdCount=5"
                                   "&Matcher.HttpCode=200,302"
                                   "&Protocol=HTTP"
                                   "&Port=8888"
                                   "&VpcId={my_vpc}"
                                   "&TargetType=instance"
                                   "&Version=2015-12-01".format(my_vpc=vpc_ids[0], lb_name="Hw2ExtensionLoadBalancer"),
                                  auth=auth2)

print_request_and_response(response_task_5_2, "messages.txt")
root = ET.fromstring(response_task_5_2.text)
target_group_arns = []
if response_task_5_2.status_code == requests.codes.ok:
    arns = root.findall('.//{http://elasticloadbalancing.amazonaws.com/doc/2015-12-01/}TargetGroupArn')
    for arn in arns:
        target_group_arns.append(arn.text)

auth2 = AWS4Auth(access_key, secret_key, 'us-east-1', 'elasticloadbalancing')

response_task_6_1 = requests.request("GET",
                                  url="https://elasticloadbalancing.amazonaws.com/?Action=CreateListener"
                                   "&LoadBalancerArn={lb_arn}"
                                   "&Protocol=HTTP"
                                   "&Port=8888"
                                   "&DefaultActions.member.1.Type=forward"
                                   "&DefaultActions.member.1.TargetGroupArn={tg_arn}"
                                   "&Version=2015-12-01".format(lb_arn = load_balancer_arns[0], tg_arn=target_group_arns[0]),
                                  auth=auth2)

print_request_and_response(response_task_6_1, "messages.txt")

auth3 = AWS4Auth(access_key, secret_key, 'us-east-1', 'autoscaling')
auto_scale_group_name = "Hw2ExtensionAutoScaling"

response_task_7_1 = requests.request("GET",
                                  url="http://autoscaling.us-east-1.amazonaws.com/"
                                   "?Action=CreateAutoScalingGroup"
                                   "&AutoScalingGroupName={grp_name}"
                                   "&TargetGroupARNs.member.1={lb_name}"
                                   "&VPCZoneIdentifier={sub1},{sub2}"
                                   "&HealthCheckGracePeriod=300"
                                   "&MinSize=1"
                                   "&MaxSize=3"
                                   "&DesiredCapacity=1"
                                   "&DefaultCooldown=30"
                                   "&LaunchTemplate.LaunchTemplateName={lt_name}"
                                   "&LaunchTemplate.Version=$Default"
                                   "&Version=2011-01-01".format(grp_name=auto_scale_group_name, 
                                                                lt_name="Hw2Extension",
                                                               lb_name=target_group_arns[0], sub1=subnet_ids[0],
                                                               sub2=subnet_ids[1]),
                                  auth=auth3)

print_request_and_response(response_task_7_1, "messages.txt")

auth3 = AWS4Auth(access_key, secret_key, 'us-east-1', 'autoscaling')
auto_scale_group_name = "Hw2ExtensionAutoScaling"

response_task_7_2 = requests.request("GET",
                                    url="http://autoscaling.us-east-1.amazonaws.com/"
                                    "?Action=PutScalingPolicy"
                                    "&AutoScalingGroupName={asg_name}"
                                    "&PolicyName=Hw2ExtensionPolicy"
                                    "&PolicyType=TargetTrackingScaling"
                                    "&TargetTrackingConfiguration.TargetValue={cpu_util}"
                                    "&TargetTrackingConfiguration.PredefinedMetricSpecification.PredefinedMetricType=ASGAverageCPUUtilization"
                                    "&TargetTrackingConfiguration.ScaleOutCooldown=200"
                                    "&TargetTrackingConfiguration.ScaleInCooldown=200"
                                    "&Version=2011-01-01"
                                    "&DryRun=true".format(asg_name=auto_scale_group_name, cpu_util=avg_cpu_utilization),
                                    auth=auth3)

print_request_and_response(response_task_7_2, "messages.txt")

print("Load Balancer URL:")
print("http://" + load_balancer_urls[0] + ":8888")


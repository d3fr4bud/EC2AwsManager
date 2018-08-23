#!/usr/bin/env python
import boto3
import sys
import colorama
from termcolor import colored
from prettytable import PrettyTable
from botocore.exceptions import ClientError


def init():
    """
    Initialize access parameter for AWS.
    Return access session to AWS Account.
    """
    colorama.init()
    session = boto3.Session(
        aws_access_key_id="AWS_ACCESS_KEY",
        aws_secret_access_key="AWS_SECRET_ACCESS_KEY",
    )

    return session


def help():
    print("USAGE: python awsmanager.py [regions/instances/action/info] [instance_id region] [start/stop/termintate]\n")
    print("EXAMPLES:")
    print("Android     : python awsmanager.py action INSTANCE_ID REGION [start/stop/termintate]")
    print("Android     : python awsmanager.py info INSTANCE_ID REGION ")
    print("MORE SPECS:")
    print("Regions Details     : python awsmanager.py regions")
    print("Instances List      : python awsmanager.py instances")
    print("\n")


def progress(count, total, status=''):
    """
    Method to manage ProgressBar
    :param count: actual step
    :param total: total steps
    :param status: String to print in progress bar
    """
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = '#' * filled_len + '-' * (bar_len - filled_len)

    sys.stdout.write('%s [%s] %s%s\r' % (status, bar, percents, '%'))
    sys.stdout.flush()


def list_instances(session):
    """
    Method prints list of all EC2 AWS Instance configured on your amazon account.
    It searches on each region and print table with most important values.
    Of course you can add other info by consulting guide for python api from AWS support.

    :param session: session object returned by init method
    :return: print list of AWS instance
    """
    try:
        t = PrettyTable(['Region', 'Id', 'State', 'Launched', 'KeyName', 'Ip Address'])

        ec2 = session.client('ec2', 'eu-west-1')
        regions = [region['RegionName'] for region in ec2.describe_regions()['Regions']]

        count = 0
        for reg in regions:
            progress(count, len(regions), "Searching AWS Ec2 Instances ...")
            ec2_ = session.resource('ec2', reg)
            istanze = ec2_.instances.all()
            if len(list(istanze)) != 0:
                for instance in istanze:
                    t.add_row([
                        colored(reg, "white"),
                        colored(instance.id, "cyan"),
                        colored(instance.state['Name'], "yellow"),
                        colored(instance.launch_time, "cyan"),
                        colored(instance.key_name, "cyan"),
                        colored(instance.public_ip_address, "white")
                    ])
            count = count + 1

        print t
    except Exception as e:
        print e


def get_instance_info(session, instance_id, region):
    """
    Methods print most important info of EC2 AWS machine you choose

    :param session: session object returned by init method
    :param instance_id: from the ec2 aws machine you would info
    :param region: from the ec2 aws machine you would info
    :return: most important info of ec2 aws machine you choose
    """
    ec2 = session.resource('ec2', region)
    instance = ec2.Instance(instance_id)
    t = PrettyTable(['Region', 'Id', 'State', 'Launched', 'KeyName', 'Ip Address'])
    t.add_row([
        colored(region, "white"), colored(instance.id, "cyan"),
        colored(instance.state['Name'], "yellow"),
        colored(instance.launch_time, "cyan"),
        colored(instance.key_name, "cyan"),
        colored(instance.public_ip_address, "white")
    ])

    print t


def list_regions(session):
    """
    Methods that prints all available regions of your amazon aws account
    :param session: session object returned by init method
    :return: print available regions
    """
    ec2 = session.client('ec2', 'eu-west-1')
    t = PrettyTable(['Region'])
    for region in ec2.describe_regions()['Regions']:
        print t.add_row([colored(region['RegionName'], "yellow")])

    print t


def instance_actions(session, instance_id, region, action):
    """
    Method to manage command to send to Amazon AWS Rest API.
    For now, I manage only start, stop and terminate.
    After sending command, method call list_instances to see pending actions.

    :param session: session object returned by init method
    :param instance_id: of aws machine you choose to manage
    :param region: of aws machine you choose to manage
    :param action: action that you want to do
    :return: print Response of requested action sended to amazon.
    """
    ec2 = session.client('ec2', region)

    if action == 'start':
        # Do a dryrun first to verify permissions
        try:
            ec2.start_instances(InstanceIds=[instance_id], DryRun=True)
        except ClientError as e:
            if 'DryRunOperation' not in str(e):
                raise

        # Dry run succeeded, run start_instances without dryrun
        try:
            response = ec2.start_instances(InstanceIds=[instance_id], DryRun=False)
            print(response)
        except ClientError as e:
            print(e)
    elif action == "stop":
        # Do a dryrun first to verify permissions
        try:
            ec2.stop_instances(InstanceIds=[instance_id], DryRun=True)
        except ClientError as e:
            if 'DryRunOperation' not in str(e):
                raise

        # Dry run succeeded, call stop_instances without dryrun
        try:
            response = ec2.stop_instances(InstanceIds=[instance_id], DryRun=False)
            print(response)
        except ClientError as e:
            print(e)

    elif action == "terminate":
        # Do a dryrun first to verify permissions
        try:
            ec2.terminate_instances(InstanceIds=[instance_id], DryRun=True)
        except ClientError as e:
            if 'DryRunOperation' not in str(e):
                raise

        # Dry run succeeded, call stop_instances without dryrun
        try:
            response = ec2.terminate_instances(InstanceIds=[instance_id], DryRun=False)
            print(response)
        except ClientError as e:
            print(e)


def main(argv):
    """
    Method take arguments from command lines and do the commands displayed on help print.
    :param argv: arguments from commandline
    :return: prints the output of command sended through terminal
    """
    param = argv[1]

    session = init()

    if param == 'regions':
        list_regions(session)

    elif param == 'instances':
        list_instances(session)

    elif param == 'info':
        if argv[2] != "" and argv[3]:
            get_instance_info(session, argv[2], argv[3])
        else:
            print "Missing Parameters for info. See USAGE"

    elif param == 'action':
        if argv[2] != "" and argv[3] != "" and argv[4] != "":
            instance_actions(session, argv[2], argv[3], argv[4])
            get_instance_info(session, argv[2], argv[3])
        else:
            print "Missing Parameters for action. See USAGE"

    elif param == 'help':
        help()
    else:
        print "Wrong Command or Option, see USAGE.\n"
        help()


if __name__ == "__main__":
    # Check arguments from terminal
    if len(sys.argv) < 2:
        help()
    else:
        main(sys.argv[0:])

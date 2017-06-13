import argparse
import sys
from configparser import ConfigParser

from ocflib.misc.mail import send_problem_report
from slackclient import SlackClient
from twisted.internet import reactor
from twisted.internet import ssl
from twisted.python import log

from slackbridge.factories import BridgeBotFactory

IRC_HOST = 'dev-irc.ocf.berkeley.edu'
IRC_PORT = 6697


def main():
    parser = argparse.ArgumentParser(
        description='OCF IRC to Slack bridge',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        '-c',
        '--config',
        default='/etc/ocf-slackbridge/slackbridge.conf',
        help='Config file to read from.',
    )
    args = parser.parse_args()

    conf = ConfigParser()
    conf.read(args.config)

    # Slack configuration
    slack_token = conf.get('slack', 'token')
    slack_uid = conf.get('slack', 'user')
    sc = SlackClient(slack_token)

    # Get all channels from Slack
    # TODO: Remove duplication between here and the user selection part
    # This should just be made into a generic Slack API call method
    results = sc.api_call('channels.list', exclude_archived=1)
    if results['ok']:
        channels = results['channels']
        slack_channel_names = [c['name'] for c in channels]
    else:
        send_problem_report('Error fetching channels from Slack API')
        sys.exit(1)

    # Get all users from Slack
    # results = sc.api_call('users.list')
    #  if results['ok']:
    #     users = [m for m in results['members'] if not m['is_bot'] and not
    #              m['deleted'] and m['name'] != 'slackbot']
    #  else:
    #     send_problem_report('Error fetching users from Slack API')
    #     sys.exit(1)

    log.startLogging(sys.stdout)

    # Main IRC bot thread
    nickserv_pass = conf.get('irc', 'nickserv_pass')
    bridge_factory = BridgeBotFactory(
        sc, nickserv_pass, slack_uid, slack_channel_names)
    reactor.connectSSL(IRC_HOST, IRC_PORT, bridge_factory,
                       ssl.ClientContextFactory())
    reactor.run()


if __name__ == '__main__':
    main()
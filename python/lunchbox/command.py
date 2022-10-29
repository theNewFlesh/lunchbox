import click

import lunchbox.tools as lbt
# ------------------------------------------------------------------------------

'''
Command line interface to lunchbox library
'''

@click.group()
def main():
    pass

@main.command()
@click.argument('url', type=str, nargs=1)
@click.argument('channel', type=str, nargs=1)
@click.argument('message', type=str, nargs=1)
def slack(url, channel, message):
    '''
        Posts a slack message to a given channel.

          URL     - https://hooks.slack.com/services URL

          CHANNEL - slack channel name

          MESSAGE - message to be posted
    '''
    lbt.post_to_slack(url, channel, message)


if __name__ == '__main__':
    main()

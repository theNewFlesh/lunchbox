import subprocess

import click

import lunchbox.theme as lbc
import lunchbox.tools as lbt
# ------------------------------------------------------------------------------

'''
Command line interface to lunchbox library
'''

click.Context.formatter_class = lbc.ThemeFormatter


@click.group()
def main():
    pass


@main.command()
@click.argument('url', type=str, nargs=1)
@click.argument('channel', type=str, nargs=1)
@click.argument('message', type=str, nargs=1)
def slack(url, channel, message):
    '''
    {white}Posts a slack message to a given channel.{clear}

    \b
    {cyan2}ARGUMENTS{clear}
           {cyan2}url{clear}  https://hooks.slack.com/services URL
       {cyan2}channel{clear}  slack channel name
       {cyan2}message{clear}  message to be posted
    '''
    lbt.post_to_slack(url, channel, message)


@main.command()
def bash_completion():
    '''
    {white}BASH completion code to be written to a _lunchbox completion file.{clear}
    '''
    cmd = '_LUNCHBOX_COMPLETE=bash_source lunchbox'
    result = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    result.wait()
    click.echo(result.stdout.read())


@main.command()
def zsh_completion():
    '''
    {white}ZSH completion code to be written to a _lunchbox completion file.{clear}
    '''
    cmd = '_LUNCHBOX_COMPLETE=zsh_source lunchbox'
    result = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    result.wait()
    click.echo(result.stdout.read())


if __name__ == '__main__':
    main()

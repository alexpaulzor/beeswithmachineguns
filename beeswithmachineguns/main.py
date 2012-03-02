#!/bin/env python

"""
The MIT License

Copyright (c) 2010 The Chicago Tribune & Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

import bees
import re
import sys
from optparse import OptionParser, OptionGroup

NO_TRAILING_SLASH_REGEX = re.compile(r'^.*?\.\w+$')

def parse_options():
    """
    Handle the command line arguments for spinning up bees
    """
    command = sys,
    parser = OptionParser(usage="""
bees COMMAND [options]

Bees with Machine Guns

A utility for arming (creating) many bees (small EC2 instances) to attack
(load test) targets (web applications).

commands:
  up      Start a batch of load testing servers.
  attack  Begin the attack on a specific url.
  down    Shutdown and deactivate the load testing servers.
  report  Report the status of the load testing servers.
  shell   Run a command on each bee.
    """)
    
    general_group = OptionGroup(parser, "general", """General options for all commands""")
    
    general_group.add_option('-f', '--file',  metavar="STATE_FILE",  nargs=1,
                        action='store', dest='statefile', type='string', default=bees.STATE_FILENAME,
                        help="The state file to use (default: ~/.bees). Note that if you use this option, you have to set it for attack, down, and report.")

    parser.add_option_group(general_group)

    up_group = OptionGroup(parser, "up", 
        """In order to spin up new servers you will need to specify at least the -k command, which is the name of the EC2 keypair to use for creating and connecting to the new servers. The bees will expect to find a .pem file with this name in ~/.ssh/.""")

    # Required
    up_group.add_option('-k', '--key',  metavar="KEY",  nargs=1,
                        action='store', dest='key', type='string', 
                        help="The ssh key pair name to use to connect to the new servers.")

    up_group.add_option('-s', '--servers', metavar="SERVERS", nargs=1,
                        action='store', dest='servers', type='int', default=5,
                        help="The number of servers to start (default: 5).")
    up_group.add_option('-g', '--group', metavar="GROUP", nargs=1,
                        action='store', dest='group', type='string', default='default',
                        help="The security group to run the instances under (default: default).")
    up_group.add_option('-z', '--zone',  metavar="ZONE",  nargs=1,
                        action='store', dest='zone', type='string', default='us-east-1d',
                        help="The availability zone to start the instances in (default: us-east-1d).")
    up_group.add_option('-i', '--instance',  metavar="INSTANCE",  nargs=1,
                        action='store', dest='instance', type='string', default='ami-ff17fb96',
                        help="The instance-id to use for each server from (default: ami-ff17fb96).")
    up_group.add_option('-l', '--login',  metavar="LOGIN",  nargs=1,
                        action='store', dest='login', type='string', default='newsapps',
                        help="The ssh username name to use to connect to the new servers (default: newsapps).")
    
    parser.add_option_group(up_group)

    attack_group = OptionGroup(parser, "attack", 
            """Beginning an attack requires only that you specify the -u option with the URL you wish to target.""")

    # Required
    attack_group.add_option('-u', '--url', metavar="URL", nargs=1,
                        action='store', dest='url', type='string',
                        help="URL of the target to attack.")

    attack_group.add_option('-n', '--number', metavar="NUMBER", nargs=1,
                        action='store', dest='number', type='int', default=1000,
                        help="The number of total connections to make to the target (default: 1000).")
    attack_group.add_option('-c', '--concurrent', metavar="CONCURRENT", nargs=1,
                        action='store', dest='concurrent', type='int', default=100,
                        help="The number of concurrent connections to make to the target (default: 100).")
    
    parser.add_option_group(attack_group)
    
    shell_group = OptionGroup(parser, "shell", """Run a command on each bee""")
    
    shell_group.add_option('-e', '--execute',  metavar="COMMAND",  nargs=1,
                        action='store', dest='command', type='string',
                        help="The command to run")

    parser.add_option_group(shell_group)

    (options, args) = parser.parse_args()

    if len(args) <= 0:
        parser.error('Please enter a command.')

    command = args[0]

    if command == 'up':
        if not options.key:
            parser.error('To spin up new instances you need to specify a key-pair name with -k')

        if options.group == 'default':
            print 'New bees will use the "default" EC2 security group. Please note that port 22 (SSH) is not normally open on this group. You will need to use to the EC2 tools to open it before you will be able to attack.'

        bees.up(options.servers, options.group, options.zone, options.instance, options.login, options.key, options.statefile)
    elif command == 'attack':
        if not options.url:
            parser.error('To run an attack you need to specify a url with -u')

        if NO_TRAILING_SLASH_REGEX.match(options.url):
            parser.error('It appears your URL lacks a trailing slash, this will disorient the bees. Please try again with a trailing slash.')

        bees.attack(options.url, options.number, options.concurrent, options.statefile)
    elif command == 'down':
        bees.down(options.statefile)
    elif command == 'report':
        bees.report(options.statefile)
    elif command == 'shell':
        if not options.command:
            parser.error('You must specify a shell command with -e')
        
        bees.shell(options.command, options.statefile)


def main():
    parse_options()


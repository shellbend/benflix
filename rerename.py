#!/usr/bin/env python

from __future__ import print_function
import re
import os
import shlex
import subprocess


# Binary Prefixes
Ki = 2**10
Mi = 2**20
Gi = 2**30


def find_incomplete(topdir, minsize=100 * Mi):
    """Find incomplete downloads, i.e. large files.
    """
    incomplete = []
    for dirpath, __, filenames in os.walk(topdir):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            filesize = os.path.getsize(filepath)
            if filesize > minsize:
                torrent = os.path.basename(os.path.dirname(filepath))
                incomplete.append(torrent)
    return incomplete


def get_qbt_log_commands(qbt_logfile):
    """Get a list of qbittorrent postprocessing commands.

    sed -n '/.*command/ s/.*command: \(.*\)/\1\/p' qbittorrent.log | sed 's/\&quot;/"/g'
    """
    pattern = re.compile(r"""
        \(N\)\s
        (?P<timestamp>
            (?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})
            T
            (?P<hour>\d{2}):(?P<minute>\d{2}):(?P<second>\d{2})
        )
        \s-\s
        Torrent:\s(?P<torrent>.*),\s
        running\sexternal\sprogram,\scommand:\s
        (?P<command>.*)$
        """, re.VERBOSE)

    commands = {}
    for line in qbt_logfile:
        m = pattern.match(line)
        if m is None:
            continue
        torrent = m.group('torrent')
        command = m.group('command')

        # Fix quotes in command
        command = re.sub(r'&quot;', '"', command)
        commands[torrent] = command
    return commands


def run_cmd(cmd):
    pid = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE)
    stdout, stderr = pid.communicate()
    return (stdout, stderr, pid.returncode)


if __name__ == '__main__':
    qbtlogfile = 'qbittorrent.log'
    with open(qbtlogfile, 'r') as f:
        cmds = get_qbt_log_commands(f)
    
    incomplete = find_incomplete('/Users/ben/torrents/completed')
    for torrent in incomplete:
        try:
            cmd = cmds[torrent]
        except KeyError:
            print('No command for torrent:', torrent)
        print('Re-running command for torrent:', torrent)
        stdout, stderr, rc = run_cmd(cmd)
        print(stdout)



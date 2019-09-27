#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import time
import subprocess
import argparse
import logging
import json


LOG_DIR = '/Users/ben/torrents'
LOG_FILE_NAME = 'qbittorrent-postprocess.log'
FILEBOT = '/usr/local/bin/filebot'
OUTPUT_DIR = '/mnt/media'
MUSIC_FORMAT = r"music/{folder.name+'/'}{file.name}"
# MOVIE_FORMAT = r"movies/{n} ({y})/{n} ({y}){' - '+vf}{' CD'+pi}{'.'+lang}"
# SERIES_FORMAT = r"shows/{n}/{episode.special ? 'Special' : 'Season '+s.pad(2)}/{n} - {episode.special ? 'S00E'+special.pad(2) : s00e00} - {t.replaceAll(/[`´‘’ʻ]/, /'/).replaceAll(/[!?.]+$/).replacePart(', Part $1')}{'.'+lang}"
MOVIE_FORMAT=r"movies/{plex.tail}"
SERIES_FORMAT=r"shows/{plex.tail}"

# LOG_DIR may not exist, which will cause logging.basicConfig to raise IOError
# If the LOG_DIR doesn't exist, don't create it, just use the current working
# directory
if not os.path.isdir(LOG_DIR):
    LOG_DIR = ''

logging.basicConfig(
    filename=os.path.join(LOG_DIR, LOG_FILE_NAME),
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)


def main():

    log = logging.getLogger(__name__)

    desc = 'Post processing script for qbittorrent and filebot AMC'

    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('-n', '--torrent-name', default='')
    parser.add_argument('-l', '--category', default='')
    parser.add_argument('-g', '--tags', default='')
    parser.add_argument('-f', '--content-path', default='')
    parser.add_argument('-r', '--root-path', default='')
    parser.add_argument('-d', '--save-path', default='')
    parser.add_argument('-c', '--number-of-files', default='')
    parser.add_argument('-z', '--torrent-size', default='')
    parser.add_argument('-t', '--tracker', default='')
    parser.add_argument('-i', '--info-hash', default='')
    parser.add_argument('-v', '--verbose', action='store_true',
        help='Log debug information.'
    )
    args = parser.parse_args()

    log.setLevel(logging.INFO)
    if args.verbose:
        log.setLevel(logging.DEBUG)

    log.info(desc)
    log.debug('Python version %d.%d.%d', *sys.version_info[:3])

    directory = args.save_path
    kind = 'single'
    if os.path.isdir(os.path.join(directory, args.torrent_name)):
        kind = 'multi'
        directory = os.path.join(directory, args.torrent_name)

    log.debug('Torrent kind: %s', kind)
    log.debug('Torrent dir: %s', directory)
    log.debug('Torrent name: %s', args.torrent_name)

    amc_log = 'amc-log-{}.txt'.format(time.strftime('%Y-%m'))
    command = [
        FILEBOT, '-script', 'fn:amc',
        '--output', OUTPUT_DIR,
        '--log-file', os.path.join(LOG_DIR, amc_log),
        '--action', 'move',
        '--conflict', 'override',
        '-non-strict',
        '--def',
            'music=y',
            'subtitles=en',
            'artwork=y',
            'deleteAfterExtract=y',
            'musicFormat=' + MUSIC_FORMAT,
            'movieFormat=' + MOVIE_FORMAT,
            'seriesFormat=' + SERIES_FORMAT,
            'ut_kind=' + kind,
            'ut_dir=' + directory,
            'ut_file=' + args.torrent_name,
            'ut_title=' + args.torrent_name,
    ]

    log.info('Running command: %s', json.dumps(command))
    try:
        output = subprocess.check_output(command)
    except subprocess.CalledProcessError as e:
        log.error('Command returned code %d\n%s\n%s',
                  e.returncode, e.cmd, e.output)
        return e.returncode
    log.info('Command output: %s', output)
    return 0

if __name__ == '__main__':
    sys.exit(main())

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import time
import subprocess
import argparse


OUTPUT_DIR = '/mnt/media'
MUSIC_FORMAT = r"music/{folder.name+'/'}{file.name}"
# MOVIE_FORMAT = r"movies/{n} ({y})/{n} ({y}){' - '+vf}{' CD'+pi}{'.'+lang}"
# SERIES_FORMAT = r"shows/{n}/{episode.special ? 'Special' : 'Season '+s.pad(2)}/{n} - {episode.special ? 'S00E'+special.pad(2) : s00e00} - {t.replaceAll(/[`´‘’ʻ]/, /'/).replaceAll(/[!?.]+$/).replacePart(', Part $1')}{'.'+lang}"
MOVIE_FORMAT=r"movies/{plex.tail}"
SERIES_FORMAT=r"shows/{plex.tail}"


def main():

    # log = open('/Users/ben/torrents/qbittorrent-postprocess.log', 'w+')

    desc = 'Post processing script for qbittorrent and filebot AMC'
    # log.write(desc + '\n')

    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('-n', '--torrent-name')
    parser.add_argument('-l', '--category')
    parser.add_argument('-g', '--tags')
    parser.add_argument('-f', '--content-path')
    parser.add_argument('-r', '--root-path')
    parser.add_argument('-d', '--save-path')
    parser.add_argument('-c', '--number-of-files')
    parser.add_argument('-z', '--torrent-size')
    parser.add_argument('-t', '--tracker')
    parser.add_argument('-i', '--info-hash')
    args = parser.parse_args()

    directory = args.save_path
    kind = 'single'
    if os.path.isdir(os.path.join(directory, args.torrent_name)):
        kind = 'multi'
        directory = os.path.join(directory, args.torrent_name)

    amc_log = 'amc-log-{}.txt'.format(time.strftime('%Y-%m'))
    command = [
        '/usr/local/bin/filebot', '-script', 'fn:amc',
        '--output', OUTPUT_DIR,
        '--log-file', os.path.join('/Users', 'ben', 'torrents', amc_log),
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

    # log.write('Running command: ' + ' '.join(command) + '\n')
    # log.close()

    return subprocess.call(command)

if __name__ == '__main__':
    sys.exit(main())

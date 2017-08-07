# tracktime
Easily track time spent on various activities.

## Installation
Once [pyinstaller](http://pyinstaller.readthedocs.io/en/stable/) is installed, a tracktime executable can be created and installed with the install script.

    pip install pyinstaller
    ./install.sh

## Usage
    usage: tracktime.py [-h] CMD [DETAIL [DETAIL ...]]
    
    Track time spent on activities.
    
    positional arguments:
      CMD         Enter a command: start, stop, or list
      DETAIL      REQUIRED for start command: specify activity@category. OPTIONAL
                  for list command: specify 'week' for a weekly summary. (default:
                  None)
    
    optional arguments:
      -h, --help  show this help message and exit
    
    examples:
        timetrack start Learn Latin@Tiny Office
                        ^^^^^^^^^^^ ^^^^^^^^^^^
                            |         |
                            |         \-----Category
                            \-----Activity
                Begins a new activity, stopping in progress activity
        tracktime stop
                Stops in progress activity
        tracktime list [week]
                Lists the Activities for the day (default), or weekly summary

## Continuous Integration Status:

[![Build Status](https://travis-ci.org/amattheisen/tracktime.svg?branch=master)](https://travis-ci.org/amattheisen/tracktime)

[![Coverage Status](https://coveralls.io/repos/github/amattheisen/tracktime/badge.svg?branch=master)](https://coveralls.io/github/amattheisen/tracktime?branch=master)

## Requirements

1. Python 2.7 or 3.x

## Miscellaneous
 * The time log is kept at `~/timelog.txt`
 * This file can be rendered via `grip` (installed with `pip install grip`).

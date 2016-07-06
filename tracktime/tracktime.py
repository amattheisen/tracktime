#!/usr/bin/env python
"""Time Track
Description: Track time spent at various activities

Author: Andrew Mattheisen

"""
from __future__ import print_function
import datetime
import argparse
from sys import argv
import fileinput
from os.path import expanduser
from os.path import join as ospathjoin

VERSION = "0.0"
TIMELOG=ospathjoin(expanduser("~"), "timelog.txt")
DATETIMEFORMAT = "%Y-%m-%dT%H:%M:%S"
DAYFORMAT = "%Y-%m-%d"
INPROGRESS = "none"
DEFAULT_CATEGORY = "general"
ACTIVITY_DAY_HEADER = """= TRACKTIME REPORT FOR {weekday:<10} {day} =
 Start - End    (Duration) | Activity@Category
---------------------------+------------------"""


# MODELS
class Activity():
    """ An Activity is a task (e.g. sweep floor) with a start datetime,
    category, and end datetime. """
    def __init__(
      self, starttime, name, category=DEFAULT_CATEGORY, endtime=False):
        self.name = name
        self.starttime = starttime
        self.category = category
        if endtime:
            self.endtime = endtime
        else:
            self.endtime = INPROGRESS

    def __str__(self):
        return "STARTTIME=%s; NAME=%s; CATEGORY=%s; ENDTIME=%s" % (
          self.starttime.strftime(DATETIMEFORMAT), self.name, self.category,
          self.endtime)

    def writedb(self):
        """ write activity to database """
        fdout = open(TIMELOG, "a")
        print(self.__str__(), file=fdout)
        fdout.close()

    def get_duration(self, now):
        """ compute the duration of activity """
        if self.endtime == INPROGRESS:
            # Task is ongoing
            duration = now - self.starttime
        else:
            duration = self.endtime - self.starttime
        return duration

    def day_format(self, now):
        """ format activity for list day output """
        # compute duration
        duration = self.get_duration(now)
        # create formatting
        if self.endtime == INPROGRESS:
            # Task is ongoing
            endtime_str = "     "
        else:
            endtime_str = "%s" % (self.endtime.strftime("%H:%M"), )
        starttime_str = " %s - " % (self.starttime.strftime("%H:%M"), )
        duration_str = "(%dh %dmin) | " % (
          duration.seconds//3600, (duration.seconds//60) % 60)
        activity_text = "%6s%5s%15s%s@%s" % (
          starttime_str, endtime_str, duration_str, self.name, self.category)
        return activity_text


# COMMANDS
def start(now, activity, category):
    """ Start a new activity. """
    activity = Activity(now, activity, category=category)
    activity.writedb()
    pass


def stop(now):
    """ Determine if there is an activity in progress and stop it. """
    # Generate a list of all activities that were started today
    today = datetime.datetime(now.year, now.month, now.day)
    activities = get_rows(now, today)
    for activity in activities:
        if activity.starttime < today:
            continue
        if activity.endtime != INPROGRESS:
            continue
        # Activity is in progress
        activity_text = activity.__str__()
        for line in fileinput.input(TIMELOG, inplace=1):
            if line.strip() != activity_text:
                print(line.strip())
                continue
            # stop activity
            log_activity = parse_line(line)
            log_activity.endtime = now.strftime(DATETIMEFORMAT)
            print(log_activity.__str__())
            break  # assumes only 1 activity in progress
        fileinput.close()
        break
    return


def list_day(day, now):
    """ print daily activity list """
    activities = get_rows(now, day)
    print(ACTIVITY_DAY_HEADER.format(
      weekday=day.strftime("%A,"), day=day.strftime(DAYFORMAT)))
    for activity in activities:
        activity_text = activity.day_format(now)
        print(activity_text)
    return


def list_week(now):
    """ print weekly activity list """
    last_sunday = datetime.datetime(
      now.year, now.month, now.day - (now.weekday() + 1))
    for ii in range(0, 7):
        this_day = last_sunday+datetime.timedelta(days=ii)
        if this_day > now:
            break
        list_day(this_day, now)
        print("")
    return


# Utilities
def parse_line(line):
    """ parse one line of the timelog. """
    if line.strip() == "" or line.strip()[0] == "#":
        return False
    (starttime, name, category, endtime) = line.split(";")
    (junk, starttime) = starttime.split("=")
    starttime = datetime.datetime.strptime(starttime, DATETIMEFORMAT)
    (junk, name) = name.split("=")
    (junk, category) = category.split("=")
    (junk, endtime) = endtime.split("=")
    endtime = endtime.strip()
    if endtime != INPROGRESS:
        endtime = datetime.datetime.strptime(endtime, DATETIMEFORMAT)
    activity = Activity(starttime, name, category, endtime)
    return activity


def get_rows(now, this_day):
    """ get rows from database """
    try:
        fdin = open(TIMELOG, "r")
    except:
        # file does not exist, nothing to list
        return []
    activities = []
    for line in fdin:
        activity = parse_line(line)
        if not activity:
            continue
        # Only lines for this_day
        if activity.starttime < this_day:
            continue
        if activity.starttime > this_day + datetime.timedelta(days=1):
            continue
        activities.append(activity)
    return activities


def make_parser():
    class CustomFormatter(
      argparse.ArgumentDefaultsHelpFormatter,
      argparse.RawDescriptionHelpFormatter):
        pass

    p = argparse.ArgumentParser(
      description='Track time spent on activities.',
      epilog="""examples: timetrack start work@desk
                          ^^^^ ^^^^
                            |    \-----Category
                            \----------Activity
            Begins a new activity, stopping in progress activity
    timetracker stop
            Stops in progress activity
    timetracker list [week]
            Lists the Activities for the day (default), or weekly summary""",
      formatter_class=CustomFormatter,
      )
    p.add_argument(
      'command', metavar='CMD', help='Enter a command: start, stop, or list')
    p.add_argument(
      'detail', nargs='*', metavar='DETAIL',
      help='''REQUIRED for start command: specify activity@category.\n
      OPTIONAL for list command: specify \'week\' for a weekly summary.''')
    return p


def parse_activity_at_category(p, args):
    """ parse activity@category - split at last '@' sign """
    try:
        if len(args.detail) > 1:
            activity = ' '.join(args.detail)
        else:
            activity = args.detail[0]
        if activity.rfind("@") > 1:
            (activity, category) = activity.rsplit("@", 1)
        else:
            category = DEFAULT_CATEGORY
    except (IndexError, NameError):
        p.error("ERROR: start command missing activity name")
    return activity, category


def read_args(argv=None):
    """ Check syntax of argv and perform requested action """
    now = datetime.datetime.now()
    p = make_parser()
    args = p.parse_args()
    if args.command == "start":
        (activity, category) = parse_activity_at_category(p, args)
        stop(now)
        print("STARTING", "TASK: ", activity, "TAG: ", category)
        start(now, activity, category)
    elif args.command == "stop":
        if len(args.detail) == 0:
            print("STOPPING CURRENT TASK")
            stop(now)
        else:
            p.error("ERROR: bad option for %s command" % args.command)
    elif args.command == "list":
        if len(args.detail) == 1 and args.detail[0] == "week":
            list_week(now)
        elif len(args.detail) == 0:
            today = datetime.datetime(now.year, now.month, now.day)
            list_day(today, now)
        else:
            p.error("ERROR: bad option for %s command" % args.command)
    else:
        p.error("ERROR: unrecognzed command")
    return


if __name__ == "__main__":
    read_args(argv)

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
TIMELOG = ospathjoin(expanduser("~"), "timelog.txt")
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
      self, starttime, name, category=DEFAULT_CATEGORY,
      endtime=False):
        self.name = name
        self.starttime = starttime
        self.category = category
        if endtime:
            self.endtime = endtime
        else:
            self.endtime = INPROGRESS

    def __str__(self):
        try:
            return "STARTTIME=%s; NAME=%s; CATEGORY=%s; ENDTIME=%s" % (
              self.starttime.strftime(DATETIMEFORMAT), self.name,
              self.category, self.endtime.strftime(DATETIMEFORMAT))
        except:  # endtime is not a datetime
            return "STARTTIME=%s; NAME=%s; CATEGORY=%s; ENDTIME=%s" % (
              self.starttime.strftime(DATETIMEFORMAT), self.name,
              self.category, self.endtime)

    def writedb(self, timelog=TIMELOG):
        """ write activity to database """
        fdout = open(timelog, "a")
        print(self.__str__(), file=fdout)
        fdout.close()

    def get_duration(self, now):
        """ compute the duration of activity """
        if self.endtime == INPROGRESS:
            # if task is for prior day
            taskday = (
              self.starttime.year, self.starttime.month, self.starttime.day)
            today = (now.year, now.month, now.day)
            if taskday != today:
                duration = datetime.datetime(
                  self.starttime.year, self.starttime.month,
                  self.starttime.day, 23, 59, 59) - self.starttime
            else:  # Task is ongoing
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
def start(now, activity, category, timelog=TIMELOG):
    """ Stop today's inprogress activity and start a new activity. """
    stop(now, timelog)
    activity = Activity(now, activity, category=category)
    activity.writedb(timelog)
    pass


def stop(now, timelog=TIMELOG):
    """ Determine if there is an activity in progress and stop it. """
    # Generate a list of all activities that were started today
    today = datetime.datetime(now.year, now.month, now.day)
    activities = get_rows(today, timelog)
    for activity in activities:
        if activity.starttime < today:
            continue
        if activity.endtime != INPROGRESS:
            continue
        # Activity is in progress
        activity_text = activity.__str__()
        for line in fileinput.input(timelog, inplace=1):
            if line.strip() != activity_text:
                print(line.strip())
                continue
            # stop activity
            log_activity = parse_line(line, timelog)
            log_activity.endtime = now.strftime(DATETIMEFORMAT)
            print(log_activity.__str__())
            break  # assumes only 1 activity in progress
        fileinput.close()
        break
    return


def list_day(day, now, timelog=TIMELOG, print_totals=True):
    """ print daily activity list """
    activities = get_rows(day, timelog)
    print(ACTIVITY_DAY_HEADER.format(
      weekday=day.strftime("%A,"), day=day.strftime(DAYFORMAT)))
    for activity in activities:
        activity_text = activity.day_format(now)
        print(activity_text)
    print("")
    if print_totals:
        print_category_hours([day], now, timelog)
    return


def list_week(now, timelog=TIMELOG):
    """ print weekly activity list """
    last_sunday = datetime.datetime(
      now.year, now.month, now.day - (now.weekday() + 1))
    days = []
    for ii in range(0, 7):
        this_day = last_sunday + datetime.timedelta(days=ii)
        if this_day > now:
            break
        list_day(this_day, now, timelog, print_totals=False)
        days.append(this_day)
    print_category_hours(days, now, timelog)
    return


def sum_category_hours(day, now, timelog=TIMELOG, category_hours=False):
    """ Sum the hours by category. """
    if not category_hours:
        category_hours = {}
    activities = get_rows(day, timelog)
    for activity in activities:
        category = activity.category
        duration = activity.get_duration(now)
        if category in category_hours:
            category_hours[category] += duration
        else:
            category_hours[category] = duration
    return category_hours


def print_category_hours(days, now, timelog=TIMELOG):
    """ Print Total hours spend in each category. """
    # Compute totals
    category_hours = {}
    for day in days:
        category_hours = sum_category_hours(day, now, timelog, category_hours)
    # Print header
    print("%44s" % "Category Totals")
    # Print category totals
    sorted_categories = list(category_hours.keys())
    sorted_categories.sort()
    for category in sorted_categories:
        duration = category_hours[category]
        duration_str = "(%dh %dmin)" % (
          duration.seconds//3600, (duration.seconds//60) % 60)
        category_summary_text = "%44s@%s" % (duration_str, category)
        print(category_summary_text)
    if len(sorted_categories) == 0:
        print("%44s" % "<no data>")


# Utilities
def parse_line(line, timelog=TIMELOG):
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


def get_rows(this_day, timelog=TIMELOG):
    """ get rows from database """
    activities = []
    try:
        with open(timelog, "r") as fdin:
            for line in fdin:
                activity = parse_line(line, timelog)
                if not activity:
                    continue
                # Only lines for this_day
                if activity.starttime < this_day:
                    continue
                if activity.starttime > this_day + datetime.timedelta(days=1):
                    continue
                activities.append(activity)
    except:  # file does not exist, nothing to list
        pass
    return activities


def make_parser():
    class CustomFormatter(
      argparse.ArgumentDefaultsHelpFormatter,
      argparse.RawDescriptionHelpFormatter):
        pass

    p = argparse.ArgumentParser(
      description='Track time spent on activities.',
      epilog="""examples: timetrack start Learn Latin@Tiny Office
                          ^^^^^^^^^^^ ^^^^^^^^^^^
                                   |    \-----Category
                                   \----------Activity
            Begins a new activity, stopping in progress activity
    tracktime stop
            Stops in progress activity
    tracktime list [week]
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
            activity = activity.strip()
            category = category.strip()
            if category == "":
                category = DEFAULT_CATEGORY
        else:
            category = DEFAULT_CATEGORY
    except (IndexError, NameError):
        p.error("ERROR: start command missing activity name")
    return activity, category


def main(argv=None):
    """ Check syntax of argv and perform requested action """
    timelog = TIMELOG
    now = datetime.datetime.now()
    p = make_parser()
    args = p.parse_args()
    if args.command == "start":
        (activity, category) = parse_activity_at_category(p, args)
        print("STARTING", "TASK: ", activity, "TAG: ", category)
        start(now, activity, category)
    elif args.command == "stop":
        if len(args.detail) == 0:
            print("STOPPING CURRENT TASK")
            stop(now, timelog)
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
    main(argv)

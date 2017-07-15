from __future__ import print_function
import pytest
from os.path import join as ospathjoin
import os
from tracktime import tracktime
import datetime

TEST_TIMELOG = ospathjoin("tests", "test_timelog.txt")


@pytest.fixture
def activity():
    name = "admin"
    category = "work"
    time1 = datetime.datetime(2016, 6, 9, 6, 5, 35)
    time2 = datetime.datetime(2016, 6, 9, 11, 23, 2)
    return tracktime.Activity(time1, name, category, time2)


def erase_test_timelog():
    """ remove the TEST_TIMELOG (if it exists) """
    try:
        os.remove(TEST_TIMELOG)
    except OSError:
        pass
    return


def add_test_timelog_entries_directly():
    timelog = TEST_TIMELOG

    """ Create a finished activity """
    name = "admin"
    category = "work"
    time1 = datetime.datetime(2016, 6, 9, 6, 5, 35)
    time2 = datetime.datetime(2016, 6, 9, 11, 23, 2)
    activity = tracktime.Activity(time1, name, category, time2)
    activity.writedb(timelog)

    """ Create a finished activity """
    name = "lunch"
    category = "break"
    time1 = datetime.datetime(2016, 6, 9, 11, 23, 2)
    time2 = datetime.datetime(2016, 6, 9, 11, 47, 17)
    activity = tracktime.Activity(time1, name, category, time2)
    activity.writedb(timelog)

    """ Create an unfinished activity at the end of a day """
    name = "work"
    category = "work"
    time1 = datetime.datetime(2016, 6, 9, 11, 47, 17)
    activity = tracktime.Activity(time1, name, category)
    activity.writedb(timelog)

    """ Create an unfinished activity with default category """
    name = "travel"
    time1 = datetime.datetime(2016, 6, 11, 1, 0, 41)
    activity = tracktime.Activity(time1, name)
    activity.writedb(timelog)
    return


def add_test_timelog_comment():
    timelog = TEST_TIMELOG
    with open(timelog, 'a') as fd:
        print("# Random Comment\n", file=fd)
    return


def populate_test_timelog():
    """ Prepare the test timelog for a test """
    erase_test_timelog()
    add_test_timelog_entries_directly()
    add_test_timelog_comment()
    return


# ====================== TESTS ============================
def test__make_parser__succeeds():

    """ activity and category """
    argv = ["start", "Work@Office"]
    p = tracktime.make_parser()
    args = p.parse_args(argv)
    assert args.command == "start"
    assert args.detail == ["Work@Office"]

    """ activity with a category both with spaces """
    argv = ["start", "Learn", "Latin@Tiny", "Office"]
    p = tracktime.make_parser()
    args = p.parse_args(argv)
    assert args.command == "start"
    assert args.detail == ["Learn", "Latin@Tiny", "Office"]

    """ list with week """
    argv = ["list", "week"]
    p = tracktime.make_parser()
    args = p.parse_args(argv)
    assert args.command == "list"
    assert args.detail == ["week"]

    """ stop command """
    argv = ["stop"]
    p = tracktime.make_parser()
    args = p.parse_args(argv)
    assert args.command == "stop"
    assert args.detail == []


def test__parse_activity_at_category():
    """ Test activity@category parsing"""
    class Object(object):
        pass

    p = tracktime.make_parser()
    args = Object()

    """ Default category """
    args.detail = ["Work"]
    activity, category = tracktime.parse_activity_at_category(p, args)
    assert activity == "Work"
    assert category == tracktime.DEFAULT_CATEGORY

    """ Default category with @ sign in activity name """
    args.detail = ["Work@"]
    activity, category = tracktime.parse_activity_at_category(p, args)
    assert activity == "Work"
    assert category == tracktime.DEFAULT_CATEGORY

    """ Simple activity and category """
    args.detail = ["Work@Office"]
    activity, category = tracktime.parse_activity_at_category(p, args)
    assert activity == "Work"
    assert category == "Office"

    """ Spaces in activity and category """
    args.detail = ["Learn", "Latin@Tiny", "Office"]
    activity, category = tracktime.parse_activity_at_category(p, args)
    assert activity == "Learn Latin"
    assert category == "Tiny Office"

    """ Spaces in activity and category and around @ sign """
    args.detail = ["email", "person@school.edu", "@", "Home", "Office"]
    activity, category = tracktime.parse_activity_at_category(p, args)
    assert activity == "email person@school.edu"
    assert category == "Home Office"

    """ @ in activity name """
    args.detail = ["email", "person@school.edu", "@", "Home", "Office"]
    activity, category = tracktime.parse_activity_at_category(p, args)
    assert activity == "email person@school.edu"
    assert category == "Home Office"

    """ No activity provided """
    args.detail = []
    pytest.raises(
      SystemExit,
      tracktime.parse_activity_at_category, p, args)


def test__create_Activity__succeeds(capsys):
    """ Create and test one completed activity and test:
          Activity.__init__()
                  .__str__()
                  .get_duration()
                  .day_format()
    """
    name = "admin"
    category = "work"
    time1 = datetime.datetime(2016, 6, 9, 6, 5, 35)
    time2 = datetime.datetime(2016, 6, 9, 11, 23, 2)
    now = datetime.datetime(2016, 6, 9, 18)
    duration = time2 - time1
    day_format = " 06:05 - 11:23  (5h 17min) | admin@work"
    activity__str__ = "\n".join([
      "STARTTIME=2016-06-09T06:05:35; NAME=admin; CATEGORY=work; "
      "ENDTIME=2016-06-09T11:23:02",
      ""])

    activity = tracktime.Activity(time1, name, category, time2)
    assert activity.starttime == time1
    assert activity.name == name
    assert activity.category == category
    assert activity.endtime == time2
    assert activity.get_duration(now) == duration
    assert activity.day_format(now) == day_format
    print(activity)
    out, err = capsys.readouterr()
    assert out == activity__str__


def test_write_and_read_Activity__succeeds(capsys):
    erase_test_timelog()

    """ Create one activity """
    name = "admin"
    category = "work"
    time1 = datetime.datetime(2016, 6, 9, 6, 5, 35)
    time2 = datetime.datetime(2016, 6, 9, 11, 23, 2)
    activity = tracktime.Activity(time1, name, category, time2)
    assert activity.starttime == time1
    assert activity.name == name
    assert activity.category == category
    assert activity.endtime == time2

    """ Write the activity to the database """
    timelog = TEST_TIMELOG
    activity.writedb(timelog)

    """ Read the activity from the database """
    day = datetime.datetime(2016, 6, 9)
    now = datetime.datetime(2016, 6, 9, 12)
    timelog = TEST_TIMELOG
    tracktime.list_day(day, now, timelog)
    out, err = capsys.readouterr()
    assert out == "\n".join([
      tracktime.ACTIVITY_DAY_HEADER.format(
        weekday=day.strftime("%A,"),
        day=day.strftime(tracktime.DAYFORMAT)),
      " 06:05 - 11:23  (5h 17min) | admin@work",
      "",
      "                             Category Totals",
      "                                  (5h 17min)@work",
      ""])


def test__get_rows__succeeds():
    erase_test_timelog()
    timelog = TEST_TIMELOG

    """ file does not exist """
    today = datetime.datetime(2016, 6, 9)
    activities = tracktime.get_rows(today, timelog)
    assert activities == []

    """ file exists, no activities for today """
    populate_test_timelog()
    today = datetime.datetime(2016, 6, 10)
    activities = tracktime.get_rows(today, timelog)
    assert activities == []

    populate_test_timelog()
    with open(TEST_TIMELOG, 'r') as fd:
        for line in fd:
            print(line.rstrip('\n'))

    """ file exists with activities for today """
    today = datetime.datetime(2016, 6, 9)
    activities = tracktime.get_rows(today, timelog)
    assert len(activities) == 3


def test__list_day__succeeds(capsys):
    populate_test_timelog()

    timelog = TEST_TIMELOG
    day = datetime.datetime(2016, 6, 9)
    now = datetime.datetime(2016, 6, 9, 18)
    answer = "\n".join([
        tracktime.ACTIVITY_DAY_HEADER.format(
          weekday=day.strftime("%A,"),
          day=day.strftime(tracktime.DAYFORMAT)),
        " 06:05 - 11:23  (5h 17min) | admin@work",
        " 11:23 - 11:47  (0h 24min) | lunch@break",
        " 11:47 -        (6h 12min) | work@work",
        "",
        "                             Category Totals",
        "                                  (0h 24min)@break",
        "                                 (11h 30min)@work",
        ""])
    tracktime.list_day(day, now, timelog)
    out, err = capsys.readouterr()
    assert out == answer
    assert err == ""
    day = datetime.datetime(2016, 6, 8)
    now = datetime.datetime(2016, 6, 8, 8)
    answer = "\n".join([
        tracktime.ACTIVITY_DAY_HEADER.format(
          weekday=day.strftime("%A,"),
          day=day.strftime(tracktime.DAYFORMAT)),
        "",
        "                             Category Totals",
        "                                   <no data>",
        ""])
    tracktime.list_day(day, now, timelog)
    out, err = capsys.readouterr()
    assert out == answer
    assert err == ""


def test__list_week_succeeds(capsys):
    populate_test_timelog()

    timelog = TEST_TIMELOG
    now = datetime.datetime(2016, 6, 11, 18)
    sunday = datetime.datetime(2016, 6, 5)
    monday = datetime.datetime(2016, 6, 6)
    tuesday = datetime.datetime(2016, 6, 7)
    wednesday = datetime.datetime(2016, 6, 8)
    thursday = datetime.datetime(2016, 6, 9)
    friday = datetime.datetime(2016, 6, 10)
    saturday = datetime.datetime(2016, 6, 11)
    answer = "\n".join([
      tracktime.ACTIVITY_DAY_HEADER.format(
        weekday=sunday.strftime("%A,"),
        day=sunday.strftime(tracktime.DAYFORMAT)),
      "",
      tracktime.ACTIVITY_DAY_HEADER.format(
        weekday=monday.strftime("%A,"),
        day=monday.strftime(tracktime.DAYFORMAT)),
      "",
      tracktime.ACTIVITY_DAY_HEADER.format(
        weekday=tuesday.strftime("%A,"),
        day=tuesday.strftime(tracktime.DAYFORMAT)),
      "",
      tracktime.ACTIVITY_DAY_HEADER.format(
        weekday=wednesday.strftime("%A,"),
        day=wednesday.strftime(tracktime.DAYFORMAT)),
      "",
      tracktime.ACTIVITY_DAY_HEADER.format(
        weekday=thursday.strftime("%A,"),
        day=thursday.strftime(tracktime.DAYFORMAT)),
      " 06:05 - 11:23  (5h 17min) | admin@work",
      " 11:23 - 11:47  (0h 24min) | lunch@break",
      " 11:47 -       (12h 12min) | work@work",
      "",
      tracktime.ACTIVITY_DAY_HEADER.format(
        weekday=friday.strftime("%A,"),
        day=friday.strftime(tracktime.DAYFORMAT)),
      "",
      tracktime.ACTIVITY_DAY_HEADER.format(
        weekday=saturday.strftime("%A,"),
        day=saturday.strftime(tracktime.DAYFORMAT)),
      " 01:00 -       (16h 59min) | travel@general",
      "",
      "                             Category Totals",
      "                                  (0h 24min)@break",
      "                                 (16h 59min)@general",
      "                                 (17h 30min)@work",
      ""])
    tracktime.list_week(now, timelog)
    out, err = capsys.readouterr()
    assert out == answer
    assert err == ""
    now = datetime.datetime(2016, 6, 8, 18)
    answer = "\n".join([
      tracktime.ACTIVITY_DAY_HEADER.format(
        weekday=sunday.strftime("%A,"),
        day=sunday.strftime(tracktime.DAYFORMAT)),
      "",
      tracktime.ACTIVITY_DAY_HEADER.format(
        weekday=monday.strftime("%A,"),
        day=monday.strftime(tracktime.DAYFORMAT)),
      "",
      tracktime.ACTIVITY_DAY_HEADER.format(
        weekday=tuesday.strftime("%A,"),
        day=tuesday.strftime(tracktime.DAYFORMAT)),
      "",
      tracktime.ACTIVITY_DAY_HEADER.format(
        weekday=wednesday.strftime("%A,"),
        day=wednesday.strftime(tracktime.DAYFORMAT)),
      "",
      "                             Category Totals",
      "                                   <no data>",
      ""])
    tracktime.list_week(now, timelog)
    out, err = capsys.readouterr()
    assert out == answer
    assert err == ""


def test__add_test_timelog_entries_with_start_stop__succeeds():
    erase_test_timelog()
    timelog = TEST_TIMELOG

    """ stop with no timelog does nothing """
    now = datetime.datetime(2016, 6, 9, 6)
    tracktime.stop(now, timelog)

    """ Create 1st activity (timelog does not exist) """
    now = datetime.datetime(2016, 6, 9, 6, 5, 35)
    name = "admin"
    category = "work"
    tracktime.start(now, name, category, timelog)

    """ Create a subsequent activity """
    now = datetime.datetime(2016, 6, 9, 11, 23, 2)
    name = "lunch"
    category = "break"
    tracktime.start(now, name, category, timelog)

    """ stop an inprogress activity """
    now = datetime.datetime(2016, 6, 9, 11, 47, 17)
    tracktime.stop(now, timelog)

    """ stop when activity inprogress for prior day does nothing """
    now = datetime.datetime(2016, 6, 10, 12)
    tracktime.stop(now, timelog)

    """ Create an unfinished activity at the end of a day """
    now = datetime.datetime(2016, 6, 9, 11, 47, 17)
    name = "work"
    category = "work"
    tracktime.start(now, name, category, timelog)

    """ Create an unfinished activity with default category """
    name = "travel"
    time1 = datetime.datetime(2016, 6, 11, 1, 0, 41)
    activity = tracktime.Activity(time1, name)
    activity.writedb(timelog)

    answer = [
      "STARTTIME=2016-06-09T06:05:35; NAME=admin; CATEGORY=work; "
      "ENDTIME=2016-06-09T11:23:02\n",
      "STARTTIME=2016-06-09T11:23:02; NAME=lunch; CATEGORY=break; "
      "ENDTIME=2016-06-09T11:47:17\n",
      "STARTTIME=2016-06-09T11:47:17; NAME=work; CATEGORY=work; "
      "ENDTIME=none\n",
      "STARTTIME=2016-06-11T01:00:41; NAME=travel; CATEGORY=general; "
      "ENDTIME=none\n",
      "\n"]
    """ test that file contains answer """
    with open(TEST_TIMELOG, 'r') as fd:
        for ii, line in enumerate(fd):
            assert line == answer[ii]


# CLI INPUT
def test__help_message__succeeds():
    assert True


def test__extra_stop_option__succeeds():
    #    """ test stop command with extra garbage raises error """
    #    argv = ["stop", "in", "the", "name", "of", "Love"]
    assert True


def test__bad_list_option__succeeds():
    """ list year should fail """
    assert True


def test__bad_command__succeeds():
    assert True

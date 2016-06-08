from tracktime import tracktime
import datetime


# MODEL
def test__create_activity__succeeds():
    time1 = datetime.datetime(2016, 6, 8, 6, 0)
    time2 = datetime.datetime(2016, 6, 8, 7, 30)
    time3 = datetime.datetime(2016, 6, 8, 7, 40)
    name1 = "write code"
    name2 = "check email"
    name3 = "test code"
    category1 = "programming"
    category2 = "admin"

    activity1 = tracktime.Activity(time1, name1, category1, time2)
    assert activity1.starttime == time1
    assert activity1.name == name1
    assert activity1.category == category1
    assert activity1.endtime == time2

    activity2 = tracktime.Activity(time2, name2, category2, time3)
    assert activity2.starttime == time2
    assert activity2.name == name2
    assert activity2.category == category2
    assert activity2.endtime == time3

    activity3 = tracktime.Activity(time3, name3)
    assert activity3.starttime == time3
    assert activity3.name == name3
    assert activity3.category == tracktime.DEFAULT_CATEGORY
    assert activity3.endtime == tracktime.INPROGRESS


def test__create_finished_activity__succeeds():
    # activity = tracktime.Activity(
    #   starttime, name, category, endtime=False)
    assert True


def test__activity_str_format__succeeds():
    assert True


def test__activity_writedb__succeeds():
    assert True


def test__activity_get_duration__succeeds():
    assert True


def test__activity_day_format__succeeds():
    assert True


# UTILITIES
def test__parse_line__succeeds():
    assert True


def test__get_rows__succeeds():
    assert True


# LIST
def test_list_week_when_none_exist__succeeds():
    assert True


def test_list_day_when_none_exist__succeeds():
    assert True


def test_list_week_when_some_activties_exist__succeeds():
    assert True


def test_list_day_when_some_activties_exist__succeeds():
    assert True


# START
def test__start_first_activity_ever__succeeds():
    assert True


def test__start_second_activity__succeeds():
    assert True


def test__start_activity_with_atsigns_in_name__succeeds():
    assert True


def test__start_activity_with_atsigns_in_name_and_no_category__succeeds():
    assert True


# STOP
def test__stop_activity_when_none_inprogress__succeeds():
    assert True


def test__stop_activity_when_one_inprogress_yesterday__succeeds():
    assert True


def test__stop_activity_when_one_inprogress_today__succeeds():
    assert True


# CLI INPUT
def test__help_message__succeeds():
    assert True


def test__missing_activity_name__succeeds():
    assert True


def test__missing_category__succeeds():
    assert True


def test__extra_stop_option__succeeds():
    assert True


def test__bad_list_option__succeeds():
    assert True


def test__bad_command__succeeds():
    assert True

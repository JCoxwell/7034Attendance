import os
from attendance.db import AttendanceDB
from datetime import datetime
from time import sleep
from unittest import TestCase

class TestAttendanceDB(TestCase):
    """
    For historical reasons, TestCase class has Java like method names.
    But, in general, you should use python coding conventions whenever possible.
    """

    # TestCase class has Java like method names
    def setUp(self):
        self.adb = AttendanceDB('test_attendance.db')

    def tearDown(self):
        # close and delete the db so next test starts clean
        self.adb.close()
        os.remove("test_attendance.db")

    def test_students(self):
        students = self.adb.get_students()
        self.assertEqual(0, len(students))
        self.adb.write_student(1234, "First Last 1", "11", "Software")
        self.adb.write_student(1235, "First Last 2", "11", "Software")
        students = self.adb.get_students()
        self.assertEqual(2, len(students))
        self.assertNotEqual(students[0][1], students[1][1])

    def test_timecards(self):
        self.adb.write_student(1234, "First Last 1", "11", "Software")
        self.adb.write_student(1235, "First Last 2", "11", "Software")
        self.adb.write_timecard(1234, datetime(2024, 10, 8, 6, 0, 0), datetime(2024, 10, 8, 9, 0, 0))
        self.adb.write_timecard(1234, datetime(2024, 10, 10, 6, 15, 0), datetime(2024, 10, 10, 9, 10, 0))
        self.adb.write_timecard(1234, datetime(2024, 10, 15, 5, 50, 0), datetime(2024, 10, 15, 9, 10, 0))
        timecards = self.adb.get_timecards(1234)
        hours = self.adb.get_total_hours(1234)
        self.assertEqual(3, len(timecards))
        self.assertEqual(9.25, hours)
        timecards = self.adb.get_timecards(1235)
        hours = self.adb.get_total_hours(1235)
        self.assertEqual(0, len(timecards))
        self.assertEqual(0, hours)

    def test_clock_in_out(self):
        self.adb.write_student(1234, "First Last 1", "11", "Software")
        self.adb.write_student(1235, "First Last 2", "11", "Software")
        self.adb.clock_in(1235)
        sleep(2)  # so time diff is not 0
        timecards = self.adb.get_timecards(1235)
        self.assertEqual(1, len(timecards))
        self.assertEqual(1235, timecards[0][0])
        self.assertIsNone(timecards[0][2])
        self.adb.clock_out(1235)
        timecards = self.adb.get_timecards(1235)
        self.assertEqual(1, len(timecards))
        self.assertEqual(1235, timecards[0][0])
        self.assertIsNotNone(timecards[0][2])
        self.assertGreater(timecards[0][3], 0)
        with self.assertRaises(Exception):
            # expected exception if not clocked in
            self.adb.clock_out(1235)

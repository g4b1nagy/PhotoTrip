import collections

from django.test import TestCase

from utils.datetime import parse_datetime, timestamp_to_datetime


class DatetimeTestCase(TestCase):
    def test_parse_datetime(self):
        TestData = collections.namedtuple("TestData", ["input", "expected"])
        test_data = [
            # Number of occurrences in test data:
            # 83728 out of 206819 => 40.48370 %
            TestData(
                input="2021:11:27 20:00:11.610+01:00",
                expected="2021-11-27T20:00:11.610000+01:00",
            ),
            # 36901 out of 206819 => 17.84217 %
            TestData(
                input="2004:05:29 18:01:45.16",
                expected="2004-05-29T18:01:45.160000+00:00",
            ),
            # 33296 out of 206819 => 16.09910 %
            TestData(
                input="2016:08:08 17:42:56.984619",
                expected="2016-08-08T17:42:56.984619+00:00",
            ),
            # 23198 out of 206819 => 11.21657 %
            TestData(
                input="2015:07:22 15:56:52Z", expected="2015-07-22T15:56:52+00:00"
            ),
            # 21508 out of 206819 => 10.39943 %
            TestData(
                input="2011:12:31 23:57:17+00:00", expected="2011-12-31T23:57:17+00:00"
            ),
            # 8041 out of 206819 => 3.88794 %
            TestData(input="2012:07:21 17:19:28", expected="2012-07-21T17:19:28+00:00"),
            # 139 out of 206819 => 0.06720 %
            TestData(
                input="2006:01:07 22:59:17.2",
                expected="2006-01-07T22:59:17.200000+00:00",
            ),
            # 7 out of 206819 => 0.00338 %
            TestData(
                input="2019:05:19 09:43:10.1Z",
                expected="2019-05-19T09:43:10.100000+00:00",
            ),
            # 1 out of 206819 => 0.00048 %
            TestData(
                input="2021:02:01 17:16:32-17:16", expected="2021-02-01T17:16:32-17:16"
            ),
        ]
        for item in test_data:
            actual = parse_datetime(item.input)
            self.assertEqual(actual.isoformat(), item.expected)
        self.assertEqual(parse_datetime("not a datetime"), None)

    def test_timestamp_to_datetime(self):
        self.assertEqual(
            timestamp_to_datetime(978310861).isoformat(), "2001-01-01T01:01:01+00:00"
        )
        # ValueError
        self.assertEqual(timestamp_to_datetime(978310861000), None)
        # OSError
        self.assertEqual(timestamp_to_datetime(97831086100000000), None)
        # OverflowError
        self.assertEqual(timestamp_to_datetime(9783108610000000000), None)

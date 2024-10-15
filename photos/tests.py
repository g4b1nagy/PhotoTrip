from django.test import TestCase

from utils.datetime import parse_datetime, extract_datetime, timestamp_to_datetime


class DatetimeTestCase(TestCase):
    def test_parse_datetime(self):
        # (input, expected)
        test_data = [
            # Number of occurrences in test data:
            # 83728 out of 206819 => 40.48370 %
            ("2021:11:27 20:00:11.610+01:00", "2021-11-27T20:00:11.610000+01:00"),
            # 36901 out of 206819 => 17.84217 %
            ("2004:05:29 18:01:45.16", "2004-05-29T18:01:45.160000+00:00"),
            # 33296 out of 206819 => 16.09910 %
            ("2016:08:08 17:42:56.984619", "2016-08-08T17:42:56.984619+00:00"),
            # 23198 out of 206819 => 11.21657 %
            ("2015:07:22 15:56:52Z", "2015-07-22T15:56:52+00:00"),
            # 21508 out of 206819 => 10.39943 %
            ("2011:12:31 23:57:17+00:00", "2011-12-31T23:57:17+00:00"),
            # 8041 out of 206819 => 3.88794 %
            ("2012:07:21 17:19:28", "2012-07-21T17:19:28+00:00"),
            # 139 out of 206819 => 0.06720 %
            ("2006:01:07 22:59:17.2", "2006-01-07T22:59:17.200000+00:00"),
            # 7 out of 206819 => 0.00338 %
            ("2019:05:19 09:43:10.1Z", "2019-05-19T09:43:10.100000+00:00"),
            # 1 out of 206819 => 0.00048 %
            ("2021:02:01 17:16:32-17:16", "2021-02-01T17:16:32+00:00"),
        ]
        for input, expected in test_data:
            actual = parse_datetime(input)
            self.assertEqual(actual.isoformat(), expected)
        self.assertEqual(parse_datetime("not a datetime"), None)

    def test_extract_datetime(self):
        # (input, expected)
        test_data = [
            ("/path/to/photos/IMG_20001231_223059.jpg", "2000-12-31T22:30:59+00:00"),
            ("/path/to/photos/PXL_20001231_223059.jpg", "2000-12-31T22:30:59+00:00"),
            ("/path/to/photos/VID_20001231_223059.jpg", "2000-12-31T22:30:59+00:00"),
            (
                "/path/to/photos/IMG_20001231_223059123.jpg",
                "2000-12-31T22:30:59.123000+00:00",
            ),
            (
                "/path/to/photos/PXL_20001231_223059123.jpg",
                "2000-12-31T22:30:59.123000+00:00",
            ),
            (
                "/path/to/photos/VID_20001231_223059123.jpg",
                "2000-12-31T22:30:59.123000+00:00",
            ),
            ("/path/to/photos/IMG-20001231.jpg", "2000-12-31T00:00:00+00:00"),
            ("/path/to/photos/VID-20001231.jpg", "2000-12-31T00:00:00+00:00"),
            ("/path/to/photos/IMG_20001231.jpg", "2000-12-31T00:00:00+00:00"),
            ("/path/to/photos/VID_20001231.jpg", "2000-12-31T00:00:00+00:00"),
            ("/path/to/photos/31 Jan 2000.jpg", "2000-01-31T00:00:00+00:00"),
            ("/path/to/photos/31-Jan-2000.jpg", "2000-01-31T00:00:00+00:00"),
            ("/path/to/photos/2000-12-31 AT 22.30.59.jpg", "2000-12-31T22:30:59+00:00"),
            ("/path/to/photos/2000-12-31 22-30-59.jpg", "2000-12-31T22:30:59+00:00"),
            ("/path/to/photos/2000-12-31 22:30:59.jpg", "2000-12-31T22:30:59+00:00"),
            ("/path/to/photos/2000-12-31-22_30_59.jpg", "2000-12-31T22:30:59+00:00"),
            (
                "/path/to/photos/2000-12-31-22H30M59S123.jpg",
                "2000-12-31T22:30:59.123000+00:00",
            ),
            ("/path/to/photos/2000-12-31-223059.jpg", "2000-12-31T22:30:59+00:00"),
            ("/path/to/photos/2000-12-31.jpg", "2000-12-31T00:00:00+00:00"),
            ("/path/to/photos/2000-12-31_22-30-59.jpg", "2000-12-31T22:30:59+00:00"),
            ("/path/to/photos/2000.12.31.jpg", "2000-12-31T00:00:00+00:00"),
            (
                "/path/to/photos/2000_12_31T22_30_59_123.jpg",
                "2000-12-31T22:30:59.123000+00:00",
            ),
            ("/path/to/photos/20001231-223059.jpg", "2000-12-31T22:30:59+00:00"),
            ("/path/to/photos/20001231_223059.jpg", "2000-12-31T22:30:59+00:00"),
            (
                "/path/to/photos/20001231_223059_123.jpg",
                "2000-12-31T22:30:59.123000+00:00",
            ),
            ("/path/to/photos/2000/foo.jpg", "2000-01-01T00:00:00+00:00"),
        ]
        for input, expected in test_data:
            actual = extract_datetime(input)
            self.assertEqual(actual.isoformat(), expected)
        # File path containing multiple datetimes
        self.assertEqual(
            extract_datetime("/path/to/photos/2000/31-Jan-2000.jpg").isoformat(),
            "2000-01-31T00:00:00+00:00",
        )
        self.assertEqual(extract_datetime("/path/to/photos/31 feb 2000.jpg"), None)

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

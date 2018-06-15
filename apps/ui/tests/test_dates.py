from django.test import TestCase

from ui.dates import due_date, date
from utils.test_utils import patch_for_test
from utils.text import fmt

from datetime import datetime, timedelta

class TestDueDate(TestCase):
    @patch_for_test('ui.dates.now')
    def setUp(self, mocked_now):
        self.now = datetime.now()
        mocked_now.return_value = self.now

    def test_more_than_seven_days_ago(self):
        when = self.now - timedelta(days=7, seconds=1)
        expected = fmt(' due %(date)s',date=date(when))
        self.assertEqual(due_date("", when), expected)

    def test_exactly_seven_days_ago(self):
        when = self.now - timedelta(days=7)
        expected = fmt(' due 7 days ago', date=date(when))
        self.assertEqual(due_date("", when), expected)

    def test_n_days_ago(self):
        when = self.now - timedelta(hours=24)
        expected = ' due 1 day ago'
        self.assertEqual(due_date("", when), expected)

        for n in range(2, 7):
            when = self.now - timedelta(days=n)
            expected = fmt(' due %(count)s days ago', count=n)
            self.assertEqual(due_date("", when), expected)

        '''
        Time differences of n days + "a fraction of a day" get returned as ' due n+1 days ago'
        '''
        when = self.now - timedelta(days=6, hours=23, minutes=59, seconds=59)
        expected = ' due 7 days ago'
        self.assertEqual(due_date("", when), expected)                

    def test_n_hours_ago(self):
        when = self.now - timedelta(minutes=60)
        expected = ' due 1 hour ago'
        self.assertEqual(due_date("", when), expected) 

        for n in range(2, 24):
            when = self.now - timedelta(hours=n)
            expected = fmt(' due %(count)s hours ago', count=n)
            self.assertEqual(due_date("", when), expected)

        when = self.now - timedelta(hours=23, minutes=30) + timedelta(seconds=1)
        expected = ' due 23 hours ago'
        self.assertEqual(due_date("", when), expected)

        when = self.now - timedelta(hours=23, minutes=30, seconds=1)
        expected = ' due 24 hours ago'
        self.assertEqual(due_date("", when), expected)

        when = self.now - timedelta(hours=23, minutes=30)
        expected = ' due 24 hours ago'
        self.assertEqual(due_date("", when), expected)               

    def test_n_minutes_ago(self):
        for n in range(2, 60):
            when = self.now - timedelta(minutes=n)
            expected = fmt(' due %(count)s minutes ago', count=n)
            self.assertEqual(due_date("", when), expected)

        when = self.now - timedelta(minutes=30, seconds=30)
        expected = ' due 31 minutes ago'
        self.assertEqual(due_date("", when), expected)

        when = self.now - timedelta(minutes=30, seconds=31)
        expected = ' due 31 minutes ago'
        self.assertEqual(due_date("", when), expected)

        when = self.now - timedelta(minutes=30, seconds=29)
        expected = ' due 30 minutes ago'
        self.assertEqual(due_date("", when), expected)

        when = self.now - timedelta(seconds=60)
        expected = ' due 1 minute ago'
        self.assertEqual(due_date("", when), expected)        

    def test_n_seconds_ago(self):
        when = self.now - timedelta(seconds=59)
        expected = ' due 59 seconds ago'
        self.assertEqual(due_date("", when), expected)

        when = self.now - timedelta(seconds=1)
        expected = ' due 1 second ago'
        self.assertEqual(due_date("", when), expected)

    def test_exactly_now(self):
        when = self.now
        expected = ' due now'
        self.assertEqual(due_date("", when), expected)

        when = self.now + timedelta(seconds=59)
        expected = ' due now'
        self.assertEqual(due_date("", when), expected)

    '''
    Due dates are displayed by the minute when the due date
    is less than 2 hours from now
    '''
    def test_n_minutes_from_now(self):
        # Test singular minute
        when = self.now + timedelta(seconds=60)
        expected = ' due in 1 minute'
        self.assertEqual(due_date("", when), expected)

        # Test that fractions of minutes get rounded off correctly
        when = self.now + timedelta(minutes=30, seconds=29)
        expected = ' due in 30 minutes'
        self.assertEqual(due_date("", when), expected)

        when = self.now + timedelta(minutes=30, seconds=30)
        expected = ' due in 31 minutes'
        self.assertEqual(due_date("", when), expected)

        when = self.now + timedelta(minutes=30, seconds=31)
        expected = ' due in 31 minutes'
        self.assertEqual(due_date("", when), expected)

        for n in range(2,120):
            when = self.now + timedelta(minutes=n)
            expected = fmt(' due in %(count)s minutes', count=n)
            self.assertEqual(due_date("", when), expected)

    '''
    Due dates are displayed by the hour when the due date 
    is less than 3 days from now
    '''
    def test_n_hours_from_now(self):
        # Test 2 hour threshold
        when = self.now + timedelta(minutes=120)
        expected = fmt(' due in 2 hours')
        self.assertEqual(due_date("", when), expected)

        # 2 hours until 71 hours
        for n in range(2, 72):
            when = self.now + timedelta(hours=n)
            expected = fmt(' due in %(count)s hours', count=n)
            self.assertEqual(due_date("", when), expected) 

        # Test that fractions of hours get rounded off correctly
        when = self.now + timedelta(hours=23, minutes=30) - timedelta(seconds=1)
        expected = ' due in 23 hours'
        self.assertEqual(due_date("", when), expected)

        when = self.now + timedelta(hours=23, minutes=30)
        expected = ' due in 24 hours'
        self.assertEqual(due_date("", when), expected)

        when = self.now + timedelta(hours=23, minutes=30, seconds=1)
        expected = ' due in 24 hours'
        self.assertEqual(due_date("", when), expected)           

    '''
    Due dates are displayed by the day when
    it is due in less than 7 days from now
    '''
    def test_n_days_from_now(self):
        # Test 3 day threshold
        when = self.now + timedelta(hours=72)
        expected = ' due in 3 days'
        self.assertEqual(due_date("", when), expected)

        # 3 days until 6 days
        for n in range(2, 7):
            when = self.now + timedelta(hours=n)
            expected = fmt(' due in %(count)s hours', count=n)
            self.assertEqual(due_date("", when), expected) 

        # Test that fractions of days get rounded off correctly
        when = self.now + timedelta(days=3, hours=12, seconds=1)
        expected = ' due in 4 days'
        self.assertEqual(due_date("", when), expected)

        when = self.now + timedelta(days=3, hours=12)
        expected = ' due in 4 days'
        self.assertEqual(due_date("", when), expected)

        when = self.now + timedelta(days=3, hours=12) - timedelta(seconds=1)
        expected = ' due in 3 days'
        self.assertEqual(due_date("", when), expected)

        when = self.now + timedelta(days=6, hours=12)
        expected = ' due in 7 days'
        self.assertEqual(due_date("", when), expected)

    '''
    Due dates are displayed as the date itself when
    it is due more than 7 days from now
    '''
    def test_more_than_seven_days_from_now(self):
        when = self.now + timedelta(days=7)
        expected = fmt(' due %(date)s', date=date(when))
        self.assertEqual(due_date("", when), expected)

        when = self.now + timedelta(days=7, seconds=1)
        expected = fmt(' due %(date)s', date=date(when))
        self.assertEqual(due_date("", when), expected)

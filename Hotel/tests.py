from datetime import datetime
from django.test import TestCase
from Hotel.models import EventBRS, ActiveIntervalsBRS, Booking

# Create your tests here.
start_date = datetime(2022, 10, 10)
finish_date = datetime(2022, 10, 14)

class GetIntervalsTestCase(TestCase):

    def test_get_intervals(self):
        """ Тест получение интервалов """
        events_by_sensor_id = EventBRS.get_by_interval(start_date, finish_date)
        intervals_by_sensor_id = ActiveIntervalsBRS.get_sensor_id_intervals_by_events_dict(events_by_sensor_id)

        print()
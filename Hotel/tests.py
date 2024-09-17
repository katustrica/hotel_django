import asyncio
from datetime import datetime
from django.test import TestCase
from Hotel.models import EventBRS, ActiveIntervalsBRS, Booking

# Create your tests here.
start_date = datetime(2022, 10, 10)
finish_date = datetime(2022, 10, 14)

class GetIntervalsTestCase(TestCase):

    def test_get_bookings(self):
        """ Тест получение интервалов """
        result = asyncio.run(Booking.get_by_interval(start_date, finish_date))
        values = sum(result.values(), [])
        self.assertEqual(len(values), 28)
        self.assertEqual(
            str(values[0]), '№20220930-16727-163995087 room(4503599627437178) 2022-09-30T16:23-2022-10-10T12:00'
        )
        self.assertEqual(
            str(values[-1]), '№20221011-16727-164800479 room(4503599627437172) 2022-10-11T14:00-2022-10-16T12:00'
        )

    def test_get_booking_by_number(self):
        """ Тест получение бронирования по номеру"""
        result = asyncio.run(Booking._get_booking_by_number('20220930-16727-163995087'))
        self.assertEqual(result.number, '20220930-16727-163995087')
        self.assertEqual(result.room_id, '4503599627437178')
        self.assertEqual(result.start, '2022-09-30T16:23')
        self.assertEqual(result.finish, '2022-10-10T12:00')

    def test_get_booking_numbers_by_interval(self):
        """ Тест номеров бронирований по интвервалу"""
        result = asyncio.run(Booking._get_booking_numbers_by_interval(start_date, finish_date))
        self.assertEqual(len(result), 28)
        self.assertEqual(result[0], '20221013-16727-159638571')
        self.assertEqual(result[-1], '20221012-16727-166176815')

    def test_get_intervals(self):
        """ Тест получение интервалов """
        events_by_sensor_id = EventBRS.get_by_interval(datetime(2024, 9, 16), datetime(2024, 9, 18))
        intervals_by_sensor_id = ActiveIntervalsBRS.get_sensor_id_intervals_by_events_dict(events_by_sensor_id)
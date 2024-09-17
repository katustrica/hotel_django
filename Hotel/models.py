import asyncio
from collections import defaultdict
from datetime import datetime, timedelta
from Hotel.const import AlarmType, API_KEY_HEADER, BOOKINGS_URL

import fdb
from django.contrib.auth.models import User
from django.db import models
from aiohttp import ClientSession


class Booking(models.Model):
    number = models.CharField(max_length=50)
    room_id = models.CharField(max_length=10)
    start = models.DateTimeField()
    finish = models.DateTimeField()

    def __str__(self):
        return f'№{self.number} room({self.room_id}) {self.start}-{self.finish}'

    def __repr__(self):
        return f'№{self.number} room({self.room_id}) {self.start}-{self.finish}'


    @classmethod
    async def get_by_interval(cls, start_date: datetime, finish_date: datetime):
        booking_numbers = await cls._get_booking_numbers_by_interval(start_date, finish_date)

        booking_infos = await asyncio.gather(
            *(asyncio.create_task(cls._get_booking_by_number(number)) for number in booking_numbers)
        )
        booking_infos_dict = defaultdict(list)
        for booking_info in booking_infos:
            booking_infos_dict[booking_info.room_id].append(booking_info)
        return booking_infos_dict

    @classmethod
    async def _get_booking_by_number(cls, booking_number):
        async with ClientSession(headers=API_KEY_HEADER) as session:
            url = f'{BOOKINGS_URL}/{booking_number}'
            async with session.get(url=url) as response:
                result = await response.json()
                room_stays = result['roomStays'][0]
                room_id = room_stays['roomId']
                start = room_stays['actualCheckInDateTime'] or room_stays['checkInDateTime']
                finish = room_stays['actualCheckOutDateTime'] or room_stays['checkOutDateTime']
                return cls(
                    number=result['number'],
                    room_id=room_id,
                    start=datetime.strptime(start, '%Y-%m-%dT%H:%M'),
                    finish=datetime.strptime(finish, '%Y-%m-%dT%H:%M')
                )

    @classmethod
    async def _get_booking_numbers_by_interval(cls, start_date: datetime, finish_date: datetime):
        async with ClientSession(headers=API_KEY_HEADER) as session:
            params = {
                'affectsPeriodFrom': f'{start_date:%Y-%m-%dT%H:%M}',
                'affectsPeriodTo': f'{finish_date:%Y-%m-%dT%H:%M}',
            }
            async with session.get(url=BOOKINGS_URL, params=params) as response:
                result = await response.json()
                return result.get('bookingNumbers') or {}


class EventBRS(models.Model):
    """ События из БРС """
    sensor_id = models.IntegerField()
    datetime = models.DateTimeField()
    type = models.IntegerField(choices=AlarmType.choices)

    def __repr__(self):
        return f'{self.sensor_id} - {self.datetime} - {"движение" if self.type == 32 else "покой"}'

    @classmethod
    def get_by_interval(cls, start_date: datetime, finish_date: datetime):
        # Соединение
        con = fdb.connect(dsn=r'83.69.116.18:c:/STRUNA-5_DB/STRUNA24.FDB',
                          user='TUKAYA88',
                          role='HOTEL',
                          password='864273')
        # Объект курсора
        cur = con.cursor()

        # Выполняем запрос
        cur.execute(f"""
            SELECT 
                d.EVENTID,
                d.MESSHIGH,
                d.DTTM, 
                d.MESSLOW
            FROM 
                DATA d
            WHERE 
                GRP = 1 
                and MDM = 1
                and DTTM >= TIMESTAMP'{start_date:%Y-%m-%d %H:%M:%S}'
                and DTTM <= TIMESTAMP'{finish_date:%Y-%m-%d %H:%M:%S}'
                and (d.MESSLOW = 21 or d.MESSLOW = 32)
        """)

        result = defaultdict(list)
        for event_id, sensor_id, event_datetime, event_type in cur.fetchall():
            result[sensor_id].append(cls(sensor_id=sensor_id, datetime=event_datetime, type=event_type))
        return result


class ActiveIntervalsBRS(models.Model):
    sensor_id = models.IntegerField()
    start = models.DateTimeField()
    finish = models.DateTimeField()

    @classmethod
    def get_sensor_id_intervals_by_events_dict(cls, sensor_id_events: dict[int, list[EventBRS]]) -> list['ActiveIntervalsBRS']:
        result = defaultdict(list)
        for sensor_id, events in sensor_id_events.items():
            if events[0].type != AlarmType.motion:
                events = events[1:]
            if events[-1].type != AlarmType.calm:
                events = events[:-1]

            start_time, finish_time = None, None
            event_count = len(events) - 1
            for start_event, finish_event in zip(events[::2], events[1::2]):
                start_time = start_event.datetime if not start_time else start_time
                finish_time = finish_event.datetime if not finish_time else finish_time

                if start_event.datetime - finish_time < timedelta(minutes=5):
                    finish_time = finish_event.datetime
                    if events.index(finish_event) == event_count:
                        result[sensor_id].append(
                            cls(sensor_id=sensor_id, start=start_time, finish=finish_time)
                        )
                else:
                    result[sensor_id].append(cls(sensor_id=sensor_id, start=start_time, finish=finish_time))
                    start_time = start_event.datetime
                    finish_time = finish_event.datetime
                    if events.index(finish_event) == event_count:
                        result[sensor_id].append(
                            cls(sensor_id=sensor_id, start=start_event.datetime, finish=finish_event.datetime)
                        )
        return result
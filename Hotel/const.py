from datetime import datetime, timedelta
from enum import IntEnum
from django.db.models import IntegerChoices

API_KEY_HEADER = {'X-API-KEY': 'f3d5fd72-747b-4f6d-904a-46188d0a9944'}
BOOKINGS_URL = r'https://partner.tlintegration.com/api/webpms/v1/bookings'
ORDER_ROOM = ['1-1,2', '2-2', '2-3', '2-4', '2-5', '2-7', '3-1', '3-2', '3-3', '3-5', '3-6', '3-7',]
MESSHIGH_NAME_DICT = {
    1: '3-5',
    2: '2-5',
    3: '2-7',
    4: '2-7',
    5: '3-7',
    6: '3-7',
    7: '1-1,2',
    8: '1-1,2',
    9: '2-3',
    10: '3-6',
    11: '2-4',
    12: '3-1',
    13: '3-1',
    14: '3-3',
    15: '2-2',
}
ROOM_ID_NAME_DICT = {
    '4503599627437168': '2-5',
    "4503599627437169": "3-1",
    # "4503599627437170": "3-2",
    "4503599627437171": "3-3",
    # "4503599627437172": "3-4",
    "4503599627437173": "3-6",
    "4503599627437174": "3-5",
    # "4503599627437175": "1-3",
    # "4503599627437176": "2-1",
    "4503599627437177": "2-2",
    "4503599627437178": "2-3",
    "4503599627437179": "2-4",
    # "4503599627437180": "2-6",
    "4503599627437181": "1-1,2",
    "4503599627437182": "2-7",
    "4503599627437183": "3-7",
}
class AlarmType(IntegerChoices):
    """ Тип события """
    motion = 32  # Технологический (движение)
    calm = 21    # Норма (нет движения)
import asyncio

import pandas as pd
import plotly.express as px
from constance import config
from django.shortcuts import render
from django.utils import timezone
from plotly.offline import plot

from Hotel.const import ROOM_ID_NAME_DICT, MESSHIGH_NAME_DICT, ORDER_ROOM
from Hotel.models import EventBRS, ActiveIntervalsBRS, Booking


def index(request):
    events_by_sensor_id = EventBRS.get_by_interval(config.START_TIME, config.FINISH_TIME)
    intervals_by_sensor_id = ActiveIntervalsBRS.get_sensor_id_intervals_by_events_dict(events_by_sensor_id)
    bookings_by_room_number = asyncio.run(Booking.get_by_interval(config.START_TIME, config.FINISH_TIME))
    plotly_tasks = []
    for bookings in bookings_by_room_number.values():
        for booking in bookings:
            name = ROOM_ID_NAME_DICT.get(booking.room_id)
            if not name:
                continue
            plotly_tasks.append(
                {'Task': f'{name}', 'Start': str(booking.start), 'Finish': str(booking.finish),
                 'Resource': 'Travelline'}
            )
    for intervals in intervals_by_sensor_id.values():
        for interval in intervals:
            name = MESSHIGH_NAME_DICT.get(interval.sensor_id)
            if not name:
                continue
            plotly_tasks.append(
                {'Task': f'{name}', 'Start': str(interval.start), 'Finish': str(interval.finish), 'Resource': 'БРС'}
            )
    discrete_map_resource = {'БРС': '#D52941', 'Travelline': '#FCD581'}
    fig = px.timeline(pd.DataFrame(plotly_tasks),
                      x_start="Start",
                      x_end="Finish",
                      y="Task",
                      color='Resource',
                      color_discrete_map=discrete_map_resource)
    fig.update_yaxes(categoryarray=ORDER_ROOM, categoryorder='array')
    now = timezone.localtime(timezone.now())
    fig.update_layout(shapes=[{'type': 'line', 'yref': 'paper', 'y0': 0, 'y1': 1, 'xref': 'x', 'x0': now, 'x1': now}])
    fig.update_layout({
        'plot_bgcolor': '#ECE7DC',
        # 'paper_bgcolor': '#FFFFF9',
    })
    fig.update_shapes(line_color="#990D35")
    gantt_plot = plot(fig, output_type="div")
    return render(request, 'index.html', context={'plot_div': gantt_plot})

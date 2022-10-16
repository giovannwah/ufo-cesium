from datetime import date, time
from typing import Optional
from strawberry_django_plus import gql


@gql.input
class DateTimeFilterInput:
    """
    Input type for filtering based on different datetime options
    """
    date_after: Optional[date] = None
    date_before: Optional[date] = None
    date_exact: Optional[date] = None
    time_after: Optional[time] = None
    time_before: Optional[time] = None
    time_exact: Optional[time] = None

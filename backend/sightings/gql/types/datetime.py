from datetime import datetime, time
from typing import Optional
from strawberry_django_plus import gql
from sightings.exceptions import DatetimeInputValidationException


@gql.input
class DateRangeFilterInput:
    """
    Input type representing a range of dates
    """
    date_start: datetime
    date_end: datetime


@gql.input
class TimeRangeFilterInput:
    """
    Input type representing a range of times
    """
    time_start: time
    time_end: time


@gql.input
class DateTimeFilterInput:
    """
    Input type for filtering based on different datetime options
    """
    datetime_after: Optional[datetime] = None
    datetime_before: Optional[datetime] = None
    datetime_exact: Optional[datetime] = None
    datetime_in_range: Optional[DateRangeFilterInput] = None
    time_after: Optional[time] = None
    time_before: Optional[time] = None
    time_exact: Optional[time] = None
    time_in_range: Optional[TimeRangeFilterInput] = None

    def validate(self) -> bool:
        """
        Return True if this DateTimeFilterInput object is valid, raise exception otherwise
        """
        if self.datetime_exact and (self.datetime_in_range or self.datetime_before or self.datetime_after):
            raise DatetimeInputValidationException('If datetimeExact is specified, no other datetime filters can be '
                                                   'specified.')
        if self.time_exact and (self.time_in_range or self.time_before or self.time_after):
            raise DatetimeInputValidationException('If timeExact is specified, no other time filter can be specified.')
        if (self.datetime_after or self.datetime_before) and self.datetime_in_range:
            raise DatetimeInputValidationException('Please don\'t use both datetimeAfter and datetimeBefore. Use '
                                                   'datetimeInRange.')
        if (self.time_after or self.time_before) and self.time_in_range:
            raise DatetimeInputValidationException('Please don\'t use both timeAfter and timeBefore. Use '
                                                   'timeInRange.')
        if (self.datetime_before and self.datetime_after) and self.datetime_before < self.datetime_after:
            raise DatetimeInputValidationException('datetimeBefore must be greater than datetimeAfter.')
        if (self.time_before and self.time_after) and self.time_before < self.time_after:
            raise DatetimeInputValidationException('timeBefore must be greater than timeAfter.')

        return True

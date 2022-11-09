from typing import Optional
from datetime import date, time
from django.db.models.query import Q
from sightings.filters.base import SimpleFilter
from sightings.exceptions import DatetimeInputValidationException
from sightings.helpers.common import prepend_to_filter_args


class DateFilter(SimpleFilter):
    def __init__(
        self,
        date_after: Optional[date],
        date_before: Optional[date],
        date_exact: Optional[date],
        pre: str = None,
    ):
        if not pre:
            raise Exception("A DateFilter requires the 'pre' prefix argument")

        self.date_after = date_after
        self.date_before = date_before
        self.date_exact = date_exact
        self.pre = pre

    def validate(self) -> bool:
        if not self.date_exact and not self.date_before and not self.date_after:
            msg = 'Must provide either dateExact or dateBefore/dateAfter arguments'
            raise DatetimeInputValidationException(msg)

        if self.date_exact and (self.date_before or self.date_after):
            msg = 'If dateExact is specified, no other date arguments can be specified.'
            raise DatetimeInputValidationException(msg)

        if (self.date_before and self.date_after) and self.date_before <= self.date_after:
            msg = 'dateBefore must be greater than dateAfter.'
            raise DatetimeInputValidationException(msg)

        return True

    def get_query(self) -> Q:
        year_exact = Q(
            **prepend_to_filter_args(self.pre, {"__year": self.date_exact.year})
        ) if self.date_exact else Q()
        month_exact = Q(
            **prepend_to_filter_args(self.pre, {"__month": self.date_exact.month})
        ) if self.date_exact else Q()
        day_exact = Q(
            **prepend_to_filter_args(self.pre, {"__day": self.date_exact.day})
        ) if self.date_exact else Q()

        exact_q = (year_exact & month_exact & day_exact)
        after_q = Q(
            **prepend_to_filter_args(self.pre, {"__gt": self.date_after})
        ) if self.date_after else Q()
        before_q = Q(
            **prepend_to_filter_args(self.pre, {"__lt": self.date_before})
        ) if self.date_after else Q()

        if self.date_exact:
            return exact_q
        elif self.date_after:
            return after_q if not self.date_before else (after_q & before_q)
        else:
            return before_q


class TimeFilter(SimpleFilter):
    def __init__(
        self,
        time_after: Optional[time],
        time_before: Optional[time],
        time_exact: Optional[time],
        pre: str = None,
    ):
        if not pre:
            raise Exception("A TimeFilter requires the 'pre' prefix argument")

        self.time_after = time_after
        self.time_before = time_before
        self.time_exact = time_exact
        self.pre = pre

    def validate(self) -> bool:
        if not self.time_exact and not self.time_before and not self.time_after:
            msg = 'Must provide either timeExact or timeBefore/timeAfter arguments'
            raise DatetimeInputValidationException(msg)

        if self.time_exact and (self.time_before or self.time_after):
            msg = 'If timeExact is specified, no other time arguments can be specified.'
            raise DatetimeInputValidationException(msg)

        if (self.time_before and self.time_after) and self.time_before <= self.time_after:
            msg = 'timeBefore must be greater than timeAfter.'
            raise DatetimeInputValidationException(msg)

        return True

    def get_query(self) -> Q:
        hour_exact = Q(
            **prepend_to_filter_args(self.pre, {"__hour": self.time_exact.hour})
        ) if self.time_exact else Q()
        minute_exact = Q(
            **prepend_to_filter_args(self.pre, {"__minute": self.time_exact.minute})
        ) if self.time_exact else Q()
        second_exact = Q(
            **prepend_to_filter_args(self.pre, {"__second": self.time_exact.second})
        ) if self.time_exact else Q()

        exact_q = (hour_exact & minute_exact & second_exact)
        after_q = Q(
            **prepend_to_filter_args(self.pre, {"__time__gt": self.time_after})
        ) if self.time_after else Q()
        before_q = Q(
            **prepend_to_filter_args(self.pre, {"__time__lt": self.time_before})
        ) if self.time_before else Q()

        if self.time_exact:
            return exact_q
        elif self.time_after:
            return after_q if not self.time_before else (after_q & before_q)
        else:
            return before_q

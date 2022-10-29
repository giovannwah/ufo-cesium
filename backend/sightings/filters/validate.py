from typing import List
from sightings.filters.base import BaseFilter
from sightings.filters.sightings import (
    SightingsLocationIdsFilter,
    SightingsLocationQueryStringFilter,
    SightingsLocationExactFilter
)
from sightings.exceptions import SightingInputValidationException


def validate_filters(filters: List[BaseFilter]) -> List[bool]:
    """
    Validate a list of filter instances
    """
    if (any(isinstance(fil, SightingsLocationQueryStringFilter) for fil in filters) or
            any(isinstance(fil, SightingsLocationExactFilter) for fil in filters)) and \
            any(isinstance(fil, SightingsLocationIdsFilter) for fil in filters):
        msg = 'Cannot specify both locationIds filter and locationFilter in sightingFilter'
        raise SightingInputValidationException(msg)

    return [fil.validate() for fil in filters]

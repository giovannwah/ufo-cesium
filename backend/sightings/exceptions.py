class LocationInputValidationException(Exception):
    """
    Raise when exception occurs while validating a location
    """
    pass


class SightingInputValidationException(Exception):
    """
    Raise when exception occurs while validating a sighting
    """
    pass


class DatetimeInputValidationException(Exception):
    """
    Raise when validating a datetime input object
    """
    pass

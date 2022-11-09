class LocationInputValidationException(Exception):
    """
    Raise when exception occurs while validating a location input object
    """
    pass


class SightingInputValidationException(Exception):
    """
    Raise when exception occurs while validating a sighting input object
    """
    pass


class PostInputValidationException(Exception):
    """
    Raise when exception occurs while validating a post input object
    """
    pass


class DatetimeInputValidationException(Exception):
    """
    Raise when exception occurs while validating a datetime input object
    """
    pass


class FilterValidationException(Exception):
    """
    Raise when filter resolver's validate_filters function runs into an issue
    """
    pass




def params_to_int(qs):
    """Converts a list of strings to an integer list."""
    return [int(str_id) for str_id in qs.split(',')]

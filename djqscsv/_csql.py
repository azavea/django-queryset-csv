"""
Utilities for executing SQL-like queries on CSV data

Used internally, subject to change without notice.

This module may later be officially supported.
"""

def _identity(x):
    return x

def _transform(dataset, arg):
    if isinstance(arg, str):
        field = arg
        display_name = arg
        transformer = _identity
    else:
        field, display_name, transformer = arg
        if field is None:
            field = dataset[0][0]
    return (dataset[0].index(field), display_name, transformer)


def SELECT(dataset, *args):
    # turn the args into indices based on the first row
    index_headers = [_transform(dataset, arg) for arg in args]
    results = []

    # treat header row as special
    results += [[header[1] for header in index_headers]]

    # add the rest of the rows
    results += [[trans(datarow[i]) for i, h, trans in index_headers]
                for datarow in dataset[1:]]
    return results


def EXCLUDE(dataset, *args):
    antiargs = [value for index, value in enumerate(dataset[0])
                if index not in args and value not in args]
    return SELECT(dataset, *antiargs)


def CONSTANT(value, display_name):
    return (None, display_name, lambda x: value)
    
def AS(field, display_name):
    return (field, display_name, _identity)

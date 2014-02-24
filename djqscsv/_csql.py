"""
Utilities for executing SQL-like queries on CSV data

Used internally, subject to change without notice.

This module may later be officially supported.
"""

def _transform(dataset, arg):
    if isinstance(arg, str):
        return (dataset[0].index(arg), arg)
    elif isinstance(arg, tuple):
        return (dataset[0].index(arg[0]), arg[1])

def SELECT(dataset, *args):
    # turn the args into indices based on the first row
    index_headers = [_transform(dataset, arg) for arg in args]
    results = []

    # treat header row as special
    results += [[header[1] for header in index_headers]]

    # add the rest of the rows
    results += [[datarow[i] for i, h in index_headers]
                for datarow in dataset[1:]]
    return results

def EXCLUDE(dataset, *args):
    antiargs = [value for index, value in enumerate(dataset[0])
               if not index in args and not value in args]
    return SELECT(dataset, *antiargs)

def AS(field, display_name):
    return (field, display_name)

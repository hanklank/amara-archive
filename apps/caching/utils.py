# Amara, universalsubtitles.org
#
# Copyright (C) 2018 Participatory Culture Foundation
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see
# http://www.gnu.org/licenses/agpl-3.0.html.

"""
caching.utils -- Utility caching functions
"""

from django.core.cache import cache as default_cache

def get_or_calc(key, work_func, cache=None):
    """Shortcut for the typical cache usage pattern

    get_or_calc() is used when a cache value stores the result of a
    function.  The steps are:

    - Try cache.get(key)
    - If there is a cache miss then

      - call work_func() to calculate the value
      - store it in the cache
    """
    if cache is None:
        cache = default_cache
    cached_value = cache.get(key)
    if cached_value is not None:
        return cached_value
    calculated_value = work_func()
    cache.set(key, calculated_value)
    return calculated_value

def get_or_calc_many(keys, work_func, cache=None):
    """Like get_or_calc but with many keys

    Args:
        keys: list of keys needed
        work_func: function to call on cache misses.  It will be passed a
            key value.

    Returns: list of results, one corresponding to each key in keys

    """
    if cache is None:
        cache = default_cache
    cached_values = cache.get_many(keys)
    rv = []
    to_set = {}
    for key in keys:
        if key in cached_values:
            result = cached_values[key]
        else:
            result = work_func(key)
            to_set[key] = result
        rv.append(result)
    if to_set:
        cache.set_many(to_set)
    return rv

__all__ = [
    'get_or_calc', 'get_or_calc_many',
]

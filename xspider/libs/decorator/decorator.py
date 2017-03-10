#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created on 2017-03-2
# Project: decorator

import json
from django.http import HttpResponse


def render_json(view_func):
    """ render http response to json decorator
    """
    def wrap(request, *args, **kwargs):
        retval = view_func(request, *args, **kwargs)
        if isinstance(retval, HttpResponse):
            retval.mimetype = 'application/json; charset=utf-8'
            return retval
        else:
            js = json.dumps(retval)
            return HttpResponse(js, content_type='application/json; charset=utf-8')
    return wrap

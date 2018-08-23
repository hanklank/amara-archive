# Amara, universalsubtitles.org
#
# Copyright (C) 2016 Participatory Culture Foundation
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

from __future__ import absolute_import
import json

from django import template
from django.core.urlresolvers import reverse
from django.forms.utils import flatatt
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from utils.bunch import Bunch
import ui.siteheader
import ui.dates

register = template.Library()

@register.filter
def date(dt):
    return ui.dates.date(dt)

@register.filter
def elapsed_time(dt):
    return ui.dates.elapsed_time(dt)

@register.filter
def datetime(dt):
    return ui.dates.datetime(dt)

@register.simple_tag(takes_context=True)
def header_links(context):
    nav = context.get('nav')
    parts = []
    parts.append(u'<ul>')
    for tab in ui.siteheader.navlinks():
        if tab.name == nav:
            parts.append(u'<li class="active">{}</li>'.format(unicode(tab)))
        else:
            parts.append(u'<li>{}</li>'.format(tab))
    parts.append(u'</ul>')
    return u'\n'.join(parts)

@register.simple_tag
def dropdown(button_id):
    return format_html(
        '<ul class="dropdownMenu" role="menu" aria-labeledby="{}">', button_id)

@register.simple_tag(name='dropdown-item')
def dropdown_item(label, view_name, *args, **kwargs):
    options = extra_dropdown_item_options(kwargs)

    if options.raw_url:
        url = view_name
    else:
        url = reverse(view_name, args=args, kwargs=kwargs)

    return make_dropdown_item(label, options, {
        'href': url
    })

@register.simple_tag(name='dropdown-js-item')
def dropdown_item(label, *data, **kwargs):
    options = extra_dropdown_item_options(kwargs)

    return make_dropdown_item(label, options, {
        'href': '#',
        'data-activate-args': json.dumps(data),
    })


def make_dropdown_item(label, options, link_attrs):
    link_attrs.update({
        'tabindex': -1,
        'role': 'menuitem',
        'class': 'dropdownMenu-link',
    })

    classes = ['dropdownMenu-item']
    if options.separator:
        classes.append('separator')
    if options.extra_class:
        classes.append(options.extra_class)

    if options.icon:
        label_html = format_html('<span class="dropdownMenu-text">{}</span> <span class="icon icon-{} dropdownMenu-extra"></span>',
                                 unicode(label), options.icon)
    elif options.count:
        label_html = format_html('<span class="dropdownMenu-text">{}</span> <span class="dropdownMenu-extra">{}</span>',
                                 unicode(label), options.count)
    else:
        label_html = format_html('<span class="dropdownMenu-text">{}</span>',
                                 unicode(label))
    if options.disabled:
        link_html = format_html(
            '<span class="dropdownMenu-link disabled">{}</span>', label_html)
    else:
        link_html = format_html('<a{}>{}</a>', flatatt(link_attrs), label_html)

    return format_html('<li role="none" class="{}">{}</li>',
                       ' '.join(classes), link_html)

def extra_dropdown_item_options(kwargs):
    """
    Extract dropdown-item arguments from kwargs, leaving the rest to use for
    the reverse() call.

    This is basically a workaround for the fact that you can't have named args
    after *args, in python2.
    """
    return Bunch(separator=kwargs.pop('separator', None),
                 extra_class=kwargs.pop('class', None),
                 disabled=kwargs.pop('disabled', None),
                 icon=kwargs.pop('icon', None),
                 count=kwargs.pop('count', None),
                 raw_url=kwargs.pop('raw_url', None))

@register.simple_tag
def enddropdown():
    return format_html('</ul>')

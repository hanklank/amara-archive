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

"""ui.utils -- frontend-related classes

This module contains a few utility classes that's used by the views code.
"""

from __future__ import absolute_import
from collections import deque
from urllib import urlencode

from collections import namedtuple
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from utils.text import fmt

class Link(object):
    def __init__(self, label, view_name, *args, **kwargs):
        self.label = label
        query = kwargs.pop('query', None)
        if '/' in view_name or view_name == '#':
            # URL path passed in, don't try to reverse it
            self.url = view_name
        else:
            self.url = reverse(view_name, args=args, kwargs=kwargs)
        if query:
            self.url += '?' + urlencode(query)

    def __unicode__(self):
        return mark_safe(u'<a href="{}">{}</a>'.format(self.url, self.label))

    def __eq__(self, other):
        return (type(self) == type(other) and
                self.label == other.label and
                self.url == other.url)

class AjaxLink(Link):
    def __init__(self, label, **query_params):
        # All of our ajax links hit the current page, adding some query
        # parameters, so this constructor is optimized for that use.
        self.label = label
        self.url = '?' + urlencode(query_params)

    def __unicode__(self):
        return mark_safe(u'<a class="ajaxLink" data-href="{}">{}</a>'.format(self.url, self.label))

class CTA(Link):
    def __init__(self, label, icon, view_name, block=False,
                 disabled=False, tooltip='', *args, **kwargs):
        super(CTA, self).__init__(label, view_name, *args, **kwargs)
        self.disabled = disabled
        self.icon = icon
        self.block = block
        self.tooltip = tooltip

    def __unicode__(self):
        return self.render()

    def as_block(self):
        return self.render(block=True)

    def render(self, block=False):
        tooltip_element = u'<span data-toggle="tooltip" data-placement="top" title="{}">{}</span>'
        link_element = u'<a href="{}" class="{}"><i class="icon {}"></i> {}</a>'
        css_class = "button"
        if self.disabled:
            css_class += " disabled"
        else:
            css_class += " cta"
        if block:
            css_class += " block"
        link = link_element.format(self.url, css_class, self.icon, self.label)
        if len(self.tooltip) > 0:
            link = tooltip_element.format(self.tooltip, link)
        return mark_safe(link)

    def __eq__(self, other):
        return (isinstance(other, Link) and
                self.label == other.label and
                self.icon == other.icon and
                self.url == other.url)

class SplitCTA(CTA):
    def __init__(self, label, view_name, icon=None, block=False,
                    disabled=False, main_tooltip=None, dropdown_tooltip=None, 
                    dropdown_items=[ 'Translate [en]', 'Translate [fil]'], 
                    *args, **kwargs):
        super(SplitCTA, self).__init__(label, icon, view_name, block, disabled, main_tooltip)
        self.dropdown_tooltip = dropdown_tooltip
        self.dropdown_items = dropdown_items

    def _create_main_button(self):
        # mark-up variables
        tooltip_mu = u'<span class="{}" data-toggle="tooltip" data-placement="top" title="{}">{}</span>'
        cta_mu = u'<a href="{}" class="{}">{}{}</a>'
        icon_mu = ""

        tooltip_css_class = ""
        cta_css_class = "button"

        if self.icon:
            icon_mu = u'<i class="icon {}"></i>'.format(self.icon)

        if self.disabled:
            cta_css_class += " disabled"
        else:
            cta_css_class += " cta"

        if self.tooltip:
            if self.block:
                tooltip_css_class += "width-100"

            # just the cta element
            cta = cta_mu.format(self.url, cta_css_class, icon_mu, self.label)

            # the cta element wrapped in the tooltip span
            cta = tooltip_mu.format(tooltip_css_class, self.tooltip, cta)
        else:
            if self.block:
                cta_css_class += " block"
            # no need to wrap the cta element in the tooltip span if there's no tooltip
            cta = cta_mu.format(self.url, cta_css_class, icon_mu, self.label)

        return mark_safe(cta)

    def _create_dropdown_toggle(self):
        tooltip_mu = u'<span data-toggle="tooltip" data-placement="top" title="{}">{}</span>'
        dropdown_mu = u'<button class="{}" data-toggle="dropdown"><span class="caret"></span></button>'

        css_class = "button split-button-dropdown-toggle"

        if self.disabled:
            css_class += " disabled"
        else:
            css_class += " cta"

        if self.dropdown_tooltip:
            # just the dropdown toggle button
            dropdown_toggle = dropdown_mu.format(css_class)

            # the dropdown toggle button wrapped in the tooltip span
            dropdown_toggle = tooltip_mu.format(self.dropdown_tooltip, dropdown_toggle)
        else:
            dropdown_toggle = dropdown_mu.format(css_class)

        return mark_safe(dropdown_toggle)

    def _create_dropdown_menu(self):
        dropdown_menu_mu = u'<ul class="split-button-dropdown-menu" role="menu">{}</ul>'
        dropdown_item_mu = u'<li>{}</li>'

        dropdown_items = [ dropdown_item_mu.format(i) for i in self.dropdown_items]
        dropdown_items = ''.join(dropdown_items)

        return mark_safe(dropdown_menu_mu.format(dropdown_items))

    def render(self, block=False):
        container = u'<div class="{}">{}{}{}</div>'
        css_class = "btn-group"

        if self.block:
            css_class += " split-button-full-width"

        main_cta = self._create_main_button()
        dropdown_toggle = self._create_dropdown_toggle()
        dropdown_menu = self._create_dropdown_menu()

        return mark_safe(container.format(css_class, main_cta, dropdown_toggle, dropdown_menu))

    def __eq__(self, other):
        #TODO override this and compare the dropdowns as well
        pass

class Tab(Link):
    def __init__(self, name, label, view_name, *args, **kwargs):
        self.name = name
        super(Tab, self).__init__(label, view_name, *args, **kwargs)

    def __eq__(self, other):
        return (isinstance(other, Tab) and
                self.name == other.name and
                self.label == other.label and
                self.url == other.url)

class SectionWithCount(list):
    """Section that contains a list of things with a count in the header
    """
    header_template = _('%(header)s <span class="count">(%(count)s)</span>')
    def __init__(self, header_text):
        self.header_text = header_text

    def header(self):
        return mark_safe(fmt(self.header_template, header=self.header_text,
                             count=len(self)))

class ContextMenu(object):
    """Context menu

    Each child of ContextMenu should be a Link or MenuSeparator item
    """
    def __init__(self, initial_items=None):
        self.items = deque()
        if initial_items:
            self.extend(initial_items)

    def append(self, item):
        self.items.append(item)

    def extend(self, items):
        self.items.extend(items)

    def prepend(self, item):
        self.items.appendleft(item)

    def prepend_list(self, items):
        self.items.extendleft(reversed(items))

    def __unicode__(self):
        output = []
        output.append(u'<div class="context-menu">')
        output.append(u'<a href="#" class="dropdown-toggle" data-toggle="dropdown" role="button" aria-haspopup="true" aria-expanded="false"><span class="caret"></span></a>')
        output.append(u'<ul class="dropdown-menu">')
        for item in self.items:
            if isinstance(item, MenuSeparator):
                output.append(u'<li class="divider"></li>')
            else:
                output.append(u'<li>{}<li>'.format(unicode(item)))
        output.append(u'</ul></div>')
        return mark_safe(u'\n'.join(output))

class MenuSeparator(object):
    """Display a line to separate items in a ContextMenu."""

__all__ = [
    'Link', 'AjaxLink', 'CTA', 'Tab', 'SectionWithCount', 'ContextMenu',
    'MenuSeparator', 'SplitCTA'
]

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

import json
import logging

from django import forms
from django.forms.forms import NON_FIELD_ERRORS
from django.conf import settings
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _
from requests.auth import HTTPBasicAuth
import requests

from ui.templatetags.forms import render_field

logger = logging.getLogger(__name__)

def make_api_request(method, path, data=None):
    url = settings.WUFOO_API_BASE_URL + path
    auth = HTTPBasicAuth(settings.WUFOO_API_KEY, '')
    return requests.request(method, url, data=data, auth=auth)

def api_get_fields(form_id):
    response = make_api_request('GET', 'forms/{}/fields.json'.format(form_id))
    data = response.json()
    return data['Fields']

def submit_entry(form_id, data):
    return make_api_request('POST', 'forms/{}/entries.json'.format(form_id),
                            data=data)

class WufooForm(forms.Form):
    # Wufoo form ID
    form_id = NotImplemented
    # map wufoo field names to django field IDS
    field_map = NotImplemented

    def submit_to_wufoo(self):
        """
        Submit form data to wufoo and validate it

        After this method runs, the form will either be successfully
        submitted, or have errors
        """
        if not self.is_valid():
            return # don't bother posting to wufoo in this case
        wufoo_data = {}
        for wufoo_name, django_name in self.field_map.items():
            if django_name in self.data:
                wufoo_data[wufoo_name] = self.data[django_name]
        response = submit_entry(self.form_id, wufoo_data)
        errors_from_wufoo = {}
        try:
            data = response.json()
            success = bool(data['Success'])
            if not data['Success']:
                for error in data['FieldErrors']:
                    field_name = self.field_map[error['ID']]
                    errors_from_wufoo[field_name] = error['ErrorText']
        except Exception, e:
            logger.warning(
                'Unknown error when processing wufoo '
                'response: {}\n\n{}'.format(e, response.content),
                exc_info=True)
            self.cleaned_data = {}
            self.errors[NON_FIELD_ERRORS] = self.error_class(
                [_(u'Unknown error')])
            return
        if errors_from_wufoo:
            self.cleaned_data = {}
            for field, text in errors_from_wufoo.items():
                self.errors[field] = self.error_class([text])

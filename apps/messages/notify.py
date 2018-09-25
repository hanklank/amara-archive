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

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _

from utils.enum import Enum

Notifications = Enum('Notifications', [
    ('ROLE_CHANGED', _('Role changed')),
])

def notify_users(notification, user_list, subject, text_template, html_template,
                 context, send_email=None):
    """
    Send notification messages to a list of users

    Arguments:
        notification: member from the Notifications enum
        user_list: list/iterable of CustomUser objects to notify
        text_template: template to use for the plain text email
        html_template: template to use for the HTML email and message HTML
        context: context dict to use for the 2 templates
        send_email: Should we send an email alongside the message?  Use
            True/False to force an email to be sent or not sent.  None, the
            default means use the notify_by_email flag from CustomUser.
    """
    message = render_to_string(text_template, context)
    html_message = render_to_string(html_template, context)
    for user in user_list:
        if (not user.email or
                send_email == False or
                send_email is None and not user.notify_by_email):
            continue
        send_mail(
            subject, message, settings.DEFAULT_FROM_EMAIL, [user.email], html_message=html_message)

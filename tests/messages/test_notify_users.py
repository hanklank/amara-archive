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

import mock

import pytest

from messages.notify import notify_users, Notifications
from utils.factories import *

@pytest.fixture(autouse=True)
def mock_render_to_string(monkeypatch):
    mock_render_to_string = mock.Mock(
        side_effect=lambda template_name, context: 'render: ' + template_name)
    with mock.patch('messages.notify.render_to_string',
                    mock_render_to_string):
        yield mock_render_to_string

@pytest.fixture(autouse=True)
def mock_send_mail(monkeypatch):
    mock_send_mail = mock.Mock()
    with mock.patch('messages.notify.send_mail', mock_send_mail):
        print 'send mail: ', repr(mock_send_mail)
        yield mock_send_mail

@pytest.fixture(autouse=True)
def set_default_from(settings):
    settings.DEFAULT_FROM_EMAIL = 'test@example.com'

def test_notify_by_email(mock_send_mail):
    user = UserFactory(notify_by_email=True)
    notify_users(Notifications.ROLE_CHANGED, [user],
                        'Test subject', 'template.txt', 'template.html', {})
    assert mock_send_mail.called
    assert mock_send_mail.call_args == mock.call(
        'Test subject', 'render: template.txt', 'test@example.com',
        [user.email], html_message='render: template.html')

def test_no_email_address_set(mock_send_mail):
    user = UserFactory(notify_by_email=True, email='')
    notify_users(Notifications.ROLE_CHANGED, [user],
                        'Test subject', 'template.txt', 'template.html', {})
    assert not mock_send_mail.called

def test_notify_by_email_unset(mock_send_mail):
    user = UserFactory(notify_by_email=False)
    notify_users(Notifications.ROLE_CHANGED, [user],
                        'Test subject', 'template.txt', 'template.html', {})
    assert not mock_send_mail.called

def test_force_email(mock_send_mail):
    user = UserFactory(notify_by_email=False)
    notify_users(Notifications.ROLE_CHANGED, [user],
                        'Test subject', 'template.txt', 'template.html', {},
                 send_email=True)
    assert mock_send_mail.called

def test_force_no_email(mock_send_mail):
    user = UserFactory(notify_by_email=True)
    notify_users(Notifications.ROLE_CHANGED, [user],
                        'Test subject', 'template.txt', 'template.html', {},
                 send_email=False)
    assert not mock_send_mail.called

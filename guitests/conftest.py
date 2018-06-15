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

import os

import pytest
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

@pytest.fixture(autouse=True)
def global_fixture(db):
    pass

@pytest.fixture(scope="session")
def driver():
    return webdriver.Remote(command_executor='http://selenium:4444/wd/hub',
                            desired_capabilities=DesiredCapabilities.FIREFOX)

@pytest.fixture(scope="session")
def base_url():
    return 'http://{}/'.format(os.environ.get('GUITEST_HOSTNAME'))


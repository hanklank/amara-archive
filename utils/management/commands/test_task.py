#
# Copyright (C) 2017 Participatory Culture Foundation
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

from optparse import make_option

from django.core.management.base import BaseCommand
import django_rq

from utils import tasks


class Command(BaseCommand):
    help = u'Run a test task'
    option_list = BaseCommand.option_list + (
        make_option('-n', '--number', default=1,
                    type=int, help='Number of tasks to run'),
        make_option('-q', '--queue', dest='queue', default='default',
                    help='Choose queue to run it in'),
    )
    def handle(self, **options):
        for i in range(options['number']):
            if options['queue'] == 'default':
                tasks.test.delay()
            else:
                queue = django_rq.get_queue(options['queue'])
                queue.enqueue(tasks.test)

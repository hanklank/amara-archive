# Amara, universalsubtitles.org
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

import logging

from django_rq import job
from rq import get_current_job

logger = logging.getLogger(__name__)

@job('high')
def process_management_form(FormClass, pickle_state):
    current_job = get_current_job()

    def update_job_meta(data):
        current_job.meta.update(data)
        current_job.save_meta()

    def progress_callback(current, total):
        update_job_meta({
            'form_status': 'PROGRESS',
            'current': current,
            'total': total,
        })
    try:
        form = FormClass.restore_from_pickle_state(pickle_state)
        if not form.is_valid():
            update_job_meta({
                'form_status': 'FAILURE',
                'error_messages': [
                    unicode(e) for e in form.errors
                ]
            })
            return
        form.submit(progress_callback)
        update_job_meta({
            'form_status': 'SUCCESS',
            'message': form.message(),
            'error_messages': form.error_messages(),
        })
    except:
        logger.warn("Error processing form", exc_info=True)
        update_job_meta({
            'form_status': 'FAILURE',
        })

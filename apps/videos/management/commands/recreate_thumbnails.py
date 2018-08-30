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

from optparse import make_option
import sys

from django.core.management.base import BaseCommand

from teams.models import Team
from videos.models import Video
import time

class Command(BaseCommand):
    help = "Recreate thumbnails for videos"
    option_list = BaseCommand.option_list + (
        make_option('-a', '--all', dest='all', default=False,
                    action='store_true'),
    )

    def handle(self, *args, **options):
        for video in self.lookup_videos(args, options):
            try:
                video.s3_thumbnail.recreate_all_thumbnails()
                print video.title_display()
            except:
                print '* {}'.format(video.title_display())

    def lookup_videos(self, args, options):
        if options['all']:
            return Video.objects.all()
        try:
            # First try looking up videos by team slug
            team = Team.objects.get(slug=args[0])
            return team.videos.all()
        except Team.DoesNotExist:
            # Fall back to Video ID
            return Video.objects.filter(video_id=args[0])

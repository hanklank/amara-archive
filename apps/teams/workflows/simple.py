# Amara, universalsubtitles.org
#
# Copyright (C) 2015 Participatory Culture Foundation
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

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.shortcuts import redirect, render
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _

from teams import views as old_views
from teams import forms
from teams.behaviors import get_main_project
from teams import forms as teams_forms
from teams.models import Project
from teams.workflows import TeamWorkflow
from ui import CTA
from utils.memoize import memoize
from utils.breadcrumbs import BreadCrumb
from utils.translation import get_language_label
from .subtitleworkflows import TeamVideoWorkflow
from videos.behaviors import VideoPageCustomization, SubtitlesPageCustomization

NEWEST_MEMBERS_PER_PAGE = 10
NEWEST_VIDEOS_PER_PAGE = 7
MAX_AVAILABLE_VIDEOS = 3

class SimpleVideoView(object):
    def __init__(self, video, cta_languages, team):
        self.video = video
        self.team = team

        # TODO fix this so we can use the Split-button CTA specified in enterprise 2014
        # For now, we only take the top language of the user
        self.cta_language = cta_languages[0]  
        
    def editor_url(self):
        # return '#'
        url = reverse('subtitles:subtitle-editor', kwargs={
            'video_id': self.video.video_id,
            'language_code': self.cta_language,
        })
        return url + '?team={}'.format(self.team.slug)

    @memoize
    def cta(self):
        """Get a CTA link for this team video"""
        if self.video.language == self.cta_language:
            icon = 'icon-transcribe'
            label =  _('Transcribe [{}]').format(self.cta_language)
        else:
            icon = 'icon-translate'
            label = _('Translate [{}]').format(self.cta_language)
        
        return CTA(label, icon, self.editor_url())
    
def render_team_header(request, team):
    return render_to_string('future/header.html', {
        'team': team,
        'brand': 'future/teams/brand.html',
        'brand_url': team.get_absolute_url(),
        'primarynav': 'future/teams/primarynav.html',
    }, RequestContext(request))

def get_dashboard_videos(team, user):
    videos = team.videos.exclude(primary_audio_language_code='').order_by('-created')

    user_languages = user.get_languages()
    available_videos = []
    for video in videos[:MAX_AVAILABLE_VIDEOS]:
        video_subtitle_languages = video.languages_with_versions()
        
        cta_languages = [l for l in user_languages if l not in video_subtitle_languages]
        if (cta_languages):
            available_videos.append(SimpleVideoView(video, cta_languages, team))

    return available_videos

def dashboard(request, team):
    member = team.get_member(request.user)
    main_project = get_main_project(team)
    if not member:
        raise PermissionDenied()

    if len(request.user.get_languages()) == 0:
        return dashboard_set_languages(request, team)

    video_qs = team.videos.all().order_by('-created')
    if main_project:
        video_qs = video_qs.filter(teamvideo__project=main_project)

    newest_members = (team.members.all()
                      .order_by('-created')
                      .select_related('user')[:NEWEST_MEMBERS_PER_PAGE])

    top_languages = [
        (get_language_label(lc), count)
        for lc, count in team.get_completed_language_counts() if count > 0
    ]
    top_languages.sort(key=lambda pair: pair[1], reverse=True)

    context = {
        'team': team,
        'team_nav': 'dashboard',
        'projects': Project.objects.for_team(team),
        'selected_project': main_project,
        'top_languages': top_languages,
        'newest_members': [m.user for m in newest_members],
        'videos': video_qs[:NEWEST_VIDEOS_PER_PAGE],
        'more_video_count': max(0, video_qs.count() - NEWEST_VIDEOS_PER_PAGE),
        'video_search_form': teams_forms.VideoFiltersForm(team),
        'member_profile_url': member.get_absolute_url(),
        'breadcrumbs': [
            BreadCrumb(team),
        ],

        'dashboard_videos': get_available_videosget_dashboard_videos(team, request.user)
    }
    
    return render(request, 'future/teams/simple/dashboard.html', context)

class SimpleVideoPageCustomization(VideoPageCustomization):
    def __init__(self, team, request, video):
        self.team = team
        self.request = request
        self.sidebar = None
        self.setup_header()

    def setup_header(self):
        if self.team:
            self.header = render_team_header(self.request, self.team)
        else:
            self.header = None

class SimpleSubtitlesPageCustomization(SubtitlesPageCustomization):
    def __init__(self, request, video, subtitle_language, team):
        super(SimpleSubtitlesPageCustomization, self).__init__(request.user, video, subtitle_language)
        self.request = request
        self.team = team
        self.setup_header()

    def setup_header(self):
        if self.team:
            self.header = render_team_header(self.request, self.team)
        else:
            self.header = None

class SimpleTeamWorkflow(TeamWorkflow):
    """Workflow for basic public/private teams

    This class implements a basic workflow for teams:  Members can edit any
    subtitles, non-members can't edit anything.
    """

    type_code = 'S'
    label = _('Simple')
    api_slug = 'simple'
    
    dashboard_view = staticmethod(dashboard)
    member_view = NotImplemented

    def get_subtitle_workflow(self, team_video):
        """Get the SubtitleWorkflow for a video with this workflow.  """
        return TeamVideoWorkflow(team_video)

    def workflow_settings_view(self, request, team):
        if request.method == 'POST':
            form = forms.SimplePermissionsForm(instance=team,
                                               data=request.POST)
            if form.is_valid():
                form.save(request.user)
                messages.success(request, _(u'Workflow updated'))
                return redirect('teams:settings_workflows', team.slug)
            else:
                messages.error(request, form.errors.as_text())
        else:
            form = forms.SimplePermissionsForm(instance=team)

        return render(request, "new-teams/settings-simple-workflow.html", {
            'team': team,
            'form': form,
            'breadcrumbs': [
                BreadCrumb(team, 'teams:dashboard', team.slug),
                BreadCrumb(_('Settings'), 'teams:settings_basic', team.slug),
                BreadCrumb(_('Workflow')),
            ],
        })

    def video_page_customize(self, request, video):
        team = self.find_team_for_page(request)
        return SimpleVideoPageCustomization(team, request, video)

    def subtitles_page_customize(self, request, video, subtitle_language):
        team = self.find_team_for_page(request)
        return SimpleSubtitlesPageCustomization(request, video, subtitle_language, team)

    def find_team_for_page(self, request):
        slug = request.GET.get('team')
        if slug == self.team.slug:
            team = self.team
        else:
            try:
                team = Team.objects.get(slug=slug)
            except Team.DoesNotExist:
                return None
        if team.user_is_member(request.user):
            return team
        else:
            return None

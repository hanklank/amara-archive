# Amara, universalsubtitles.org
#
# Copyright (C) 2013 Participatory Culture Foundation
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

# import json
from django import forms
# from django.core import validators
# from django.urls import reverse
# from django.forms.utils import ErrorDict
from django.utils.translation import ugettext_lazy

from auth.models import CustomUser as User
from teams.models import Team
from externalsites import models
# from utils.forms import SubmitButtonField, SubmitButtonWidget
# from utils.text import fmt
# import videos.tasks
import logging
logger = logging.getLogger("forms")

class AccountForm(forms.ModelForm):
    def __init__(self, owner, data=None, **kwargs):
        super(AccountForm, self).__init__(data=data,
                                          instance=self.get_account(owner),
                                          **kwargs)
        self.owner = owner

    @classmethod
    def get_account(cls, owner):
        ModelClass = cls._meta.model
        try:
            return ModelClass.objects.for_owner(owner).get()
        except ModelClass.DoesNotExist:
            return None

    def save(self):
        account = forms.ModelForm.save(self, commit=False)
        if isinstance(self.owner, Team):
            account.type = models.ExternalAccount.TYPE_TEAM
            account.owner_id = self.owner.id
        elif isinstance(self.owner, User):
            account.type = models.ExternalAccount.TYPE_USER
            account.owner_id = self.owner.id
        else:
            raise TypeError("Invalid owner type: %s" % self.owner)
        account.save()
        return account

    @property
    def has_existing_account(self):
        return self.instance.pk is not None

class KalturaAccountForm(AccountForm):
    partner_id = forms.IntegerField()

    class Meta:
        model = models.KalturaAccount
        fields = ['partner_id', 'secret']

class BrightcoveCMSAccountForm(AccountForm):
    publisher_id = forms.IntegerField(label=ugettext_lazy("Publisher ID"))
    client_id = forms.CharField(label=ugettext_lazy("Client ID"))
    client_secret = forms.CharField(label=ugettext_lazy("Client Secret"))

    class Meta:
        model = models.BrightcoveCMSAccount
        fields = ['publisher_id', 'client_id', 'client_secret' ]

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import HttpResponseRedirect


class PermRequired(PermissionRequiredMixin):
    def handle_no_permission(self):
        if self.raise_exception or self.request.user.is_authenticated:
            return HttpResponseRedirect("/index/?msg=用户没有访问的权限")


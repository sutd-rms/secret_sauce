from django.contrib.auth.management.commands import createsuperuser
from django.core.management import CommandError
from django.contrib.auth import get_user_model


class Command(createsuperuser.Command):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.UserModel = get_user_model()
        self.username_field = self.UserModel._meta.get_field(self.UserModel.USERNAME_FIELD)

        omit = {'company'}
        self.UserModel.REQUIRED_FIELDS = tuple([field for field in self.UserModel.REQUIRED_FIELDS if field not in omit])

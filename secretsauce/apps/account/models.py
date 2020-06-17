from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import ugettext_lazy as _
import uuid

from secretsauce.utils import IncompatibleInvitationCode

class Company(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.name

# TODO: Hash ID field
class Invitation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(verbose_name='email', max_length=255, unique=True)

class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""

        # Ensure email corresponds to invitation
        if not email:
            raise ValueError('The given email must be set')
        if email != extra_fields.get("invitation").email:
            raise IncompatibleInvitationCode()

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""

        # Automatically create invitation and assign company (compatible with "manage.py createadmin" usage)
        invitation = Invitation.objects.get_or_create(email=email)[0]
        company = Company.objects.get_or_create(name="Revenue Management Solutions")[0]
        extra_fields.setdefault('invitation', invitation)
        extra_fields.setdefault('company', company)

        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)

class User(AbstractUser):
    username = None
    email = models.EmailField(_("email address"), unique=True, primary_key=True)
    phone = models.CharField(null=True, max_length=255)
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
    )
    invitation = models.OneToOneField(
        Invitation,
        on_delete=models.CASCADE,
    )

    # REQUIRED_FIELDS is a list of field names that will be prompted when creating a user via the createsuperuser manage.py command.
    # Djoser also uses REQUIRED_FIELDS to define which fields are required in the API, thus rendering createsuperuser hard to use
    REQUIRED_FIELDS = ['first_name', 'last_name', 'company', 'invitation']
    USERNAME_FIELD = 'email'

    objects = UserManager()

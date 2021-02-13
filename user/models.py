from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
from PIL import Image
from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.utils.translation import ugettext_lazy as _
from django.core.mail import send_mail

class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, username, name, email, password, **extra_fields):
        """メールアドレスでの登録を必須にする"""
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        username = self.model.normalize_username(username)
        name = name
        user = self.model(email=email, username=username, name=name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, email, name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(username, name, email, password, **extra_fields)

    def create_superuser(self, username, name, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(username, name, email, password, **extra_fields)
    
class User(AbstractBaseUser, PermissionsMixin):
    """カスタムユーザーモデル."""
    email = models.EmailField(_('email'), unique=True, blank=False, null=False)
    username = models.SlugField(_('username'), max_length=24, unique=True, blank=False, null=False)
    name = models.CharField(_('name'), max_length=24, blank=False, null=False)
    picture = models.ImageField(_('picture'), upload_to='profile/', default='default.png')
    intro = models.TextField(_('introduction'), max_length=400, blank=True)

    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_(
            'Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    date_joined = models.DateTimeField(_('launch'), default=timezone.now)

    objects = UserManager()

    def __str__(self):
        return self.name

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'name']

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')


    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)


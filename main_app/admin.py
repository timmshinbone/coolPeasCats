from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
# import your models here
from .models import Cat, Feeding, Toy, Photo, Profile, User

# Register your models here
admin.site.register(Cat)

admin.site.register(Feeding)

admin.site.register(Toy)

admin.site.register(Photo)


# Define an inline admin descriptor for Profile model
# which acts a bit like a singleton
class ProfileInline(admin.StackedInline):
  model = Profile
  can_delete = False
  verbose_name_plural = 'profile'

# Define a new User admin
class UserAdmin(BaseUserAdmin):
  inlines = (ProfileInline),

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
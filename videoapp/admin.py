from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Video, Rating

class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('email', 'username', 'user_type', 'is_active', 'is_staff', 'is_superuser')
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'user_type')
    search_fields = ('email', 'username')
    ordering = ('email',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('username', 'user_type')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2', 'user_type', 'is_active', 'is_staff', 'is_superuser'),
        }),
    )
    
    # Remove the `groups` and `user_permissions` from filter_horizontal
    filter_horizontal = ()

# Register User model with custom admin
admin.site.register(User, CustomUserAdmin)

# Register Video and Rating models
admin.site.register(Video)
admin.site.register(Rating)

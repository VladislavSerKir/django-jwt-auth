from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django import forms
from django.contrib import messages
from .models import User
from .enums import Role


class UserCreationForm(forms.ModelForm):
    """Form for creating user with two password fields"""
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput,
        required=True
    )
    password2 = forms.CharField(
        label='Password confirmation',
        widget=forms.PasswordInput,
        required=True
    )

    class Meta:
        model = User
        fields = ('email', 'name', 'role')

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """Form for changing user with password change field"""
    password = forms.CharField(
        label='New Password',
        widget=forms.PasswordInput,
        required=False,
        help_text="Leave empty if you don't want to change the password"
    )

    class Meta:
        model = User
        fields = ('email', 'name', 'role', 'is_active', 'password')

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get("password")
        if password:  # If new password is specified
            user.set_password(password)
        if commit:
            user.save()
        return user


@admin.register(User)
class CustomUserAdmin(admin.ModelAdmin):
    """Admin interface for custom User model with proper password handling"""

    form = UserChangeForm
    add_form = UserCreationForm

    # Define fields to display in admin
    fieldsets = (
        (None, {'fields': ('email',)}),
        (_('Personal info'), {'fields': ('name',)}),
        (_('Permissions'), {
            'fields': ('is_active', 'role'),
        }),
        (_('Change password'), {
            'fields': ('password',),
            'classes': ('collapse',),
        }),
        (_('Important dates'), {
            'fields': ('last_login', 'created_at', 'updated_at')
        }),
    )

    # Fields when creating a new user
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'role', 'password1', 'password2'),
        }),
    )

    # What to display in user list
    list_display = ('email', 'name', 'get_role_display',
                    'is_active', 'created_at')

    # Filters
    list_filter = ('is_active', 'role', 'created_at')

    # Search by these fields
    search_fields = ('email', 'name')

    # Ordering
    ordering = ('email',)

    # Read-only fields
    readonly_fields = ('last_login', 'created_at', 'updated_at')

    # Custom methods for display
    def get_role_display(self, obj):
        """Display human-readable role name"""
        try:
            return Role(obj.role).name
        except ValueError:
            return str(obj.role)
    get_role_display.short_description = 'Role'
    get_role_display.admin_order_field = 'role'

    def get_form(self, request, obj=None, **kwargs):
        """Configure form in admin"""
        form = super().get_form(request, obj, **kwargs)
        if 'role' in form.base_fields:
            form.base_fields['role'].choices = Role.choices()
        return form

    # Method to get fields when creating a new user

    def get_fieldsets(self, request, obj=None):
        if not obj:  # If creating new user
            return self.add_fieldsets
        return super().get_fieldsets(request, obj)

    # Admin actions
    actions = ['make_admin', 'make_user', 'activate_users', 'deactivate_users']

    def make_admin(self, request, queryset):
        """Make selected users administrators"""
        updated = queryset.update(role=Role.ADMIN.value)
        self.message_user(
            request,
            f'{updated} users have become administrators',
            messages.SUCCESS
        )
    make_admin.short_description = "Make administrators"

    def make_user(self, request, queryset):
        """Make selected users regular users"""
        updated = queryset.update(role=Role.USER.value)
        self.message_user(
            request,
            f'{updated} users have become regular users',
            messages.SUCCESS
        )
    make_user.short_description = "Make regular users"

    def activate_users(self, request, queryset):
        """Activate selected users"""
        updated = queryset.update(is_active=True)
        self.message_user(
            request,
            f'{updated} users have been activated',
            messages.SUCCESS
        )
    activate_users.short_description = "Activate users"

    def deactivate_users(self, request, queryset):
        """Deactivate selected users"""
        updated = queryset.update(is_active=False)
        self.message_user(
            request,
            f'{updated} users have been deactivated',
            messages.WARNING
        )
    deactivate_users.short_description = "Deactivate users"

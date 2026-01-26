from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.auth import get_user_model
from apps.users.enums import Role
from apps.notes.models import Note
import bcrypt


class Command(BaseCommand):
    help = 'Creates test users and notes using transaction'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clean',
            action='store_true',
            help='Delete existing test users before creating'
        )

    def handle(self, *args, **options):
        User = get_user_model()

        test_users = [
            {
                'name': 'System Administrator',
                'email': 'admin@example.com',
                'password': 'AdminPass123!',
                'role': Role.ADMIN,
                'notes': [
                    {'name': 'Important tasks',
                        'description': '1. Check system security\n2. Update servers\n3. Conduct audit'},
                    {'name': 'Weekly meetings',
                        'description': 'Monday: standup\nWednesday: meeting with developers\nFriday: report to management'},
                ]
            },
            {
                'name': 'Ivan Petrov',
                'email': 'ivan@example.com',
                'password': 'UserPass123!',
                'role': Role.USER,
                'notes': [
                    {'name': 'Shopping list',
                        'description': 'Milk, bread, eggs, fruits, coffee'},
                    {'name': 'Project ideas',
                        'description': '1. Add dark theme\n2. Implement PDF export\n3. Create mobile app'},
                ]
            },
            {
                'name': 'Maria Sidorova',
                'email': 'maria@example.com',
                'password': 'MariaPass123!',
                'role': Role.USER,
                'notes': [
                    {'name': 'Recipes', 'description': 'Spaghetti carbonara:\n- pasta 400g\n- bacon 200g\n- eggs 3pcs\n- parmesan 100g'},
                    {'name': 'Books to read',
                        'description': '1. "Clean Code" Robert Martin\n2. "Design Patterns" GoF\n3. "The Pragmatic Programmer"'},
                ]
            }
        ]

        try:
            with transaction.atomic():
                if options['clean']:
                    self._clean_test_data(User)

                created_users = []

                for user_data in test_users:
                    user = self._create_or_update_user(User, user_data)
                    created_users.append(user)

                    self._create_user_notes(user, user_data['notes'])

                self._print_summary(created_users)

                self.stdout.write(
                    self.style.SUCCESS('\n✅ Test data successfully created!')
                )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(
                    f'\n❌ Error creating test data: {str(e)}')
            )
            raise

    def _clean_test_data(self, User):
        """Clean test data"""
        emails_to_delete = ['admin@example.com',
                            'ivan@example.com', 'maria@example.com']

        users_deleted, _ = User.objects.filter(
            email__in=emails_to_delete).delete()

        Note.objects.filter(user__email__in=emails_to_delete).delete()

        self.stdout.write(
            self.style.WARNING(f'🗑️ Deleted {users_deleted} test records')
        )

    def _create_or_update_user(self, User, user_data):
        """Create or update user"""
        email = user_data['email']

        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            user.name = user_data['name']
            user.role = user_data['role'].value
            user.is_active = True

            if user_data.get('update_password', True):
                salt = bcrypt.gensalt()
                hashed_password = bcrypt.hashpw(
                    user_data['password'].encode('utf-8'), salt)
                user.password = hashed_password.decode('utf-8')

            user.save()
            self.stdout.write(
                self.style.WARNING(f'🔄 Updated user: {user.email}')
            )
        else:
            salt = bcrypt.gensalt()
            hashed_password = bcrypt.hashpw(
                user_data['password'].encode('utf-8'), salt)

            user = User.objects.create(
                name=user_data['name'],
                email=email,
                password=hashed_password.decode('utf-8'),
                role=user_data['role'].value,
                is_active=True
            )
            self.stdout.write(
                self.style.SUCCESS(f'✅ Created user: {user.email}')
            )

        return user

    def _create_user_notes(self, user, notes_data):
        """Create notes for user"""
        for note_data in notes_data:
            if not Note.objects.filter(user=user, name=note_data['name']).exists():
                Note.objects.create(
                    user=user,
                    name=note_data['name'],
                    description=note_data['description']
                )
                self.stdout.write(
                    self.style.SUCCESS(
                        f'   📝 Created note: "{note_data["name"]}"')
                )

    def _print_summary(self, users):
        """Print summary of created data"""
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.SUCCESS("SUMMARY OF CREATED DATA"))
        self.stdout.write("=" * 60)

        for user in users:
            notes_count = Note.objects.filter(user=user).count()
            role_name = "Administrator" if user.role == Role.ADMIN.value else "User"

            self.stdout.write(f"\n👤 {user.name}")
            self.stdout.write(f"   Email: {user.email}")
            self.stdout.write(f"   Role: {role_name}")
            self.stdout.write(f"   Notes: {notes_count}")

        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.SUCCESS("LOGIN DATA"))
        self.stdout.write("=" * 60)

        for user in users:
            if user.email == 'admin@example.com':
                password = 'AdminPass123!'
            elif user.email == 'ivan@example.com':
                password = 'UserPass123!'
            elif user.email == 'maria@example.com':
                password = 'MariaPass123!'
            else:
                password = '(password not changed)'

            role = "👑 ADMIN" if user.role == Role.ADMIN.value else "👤 USER"
            self.stdout.write(f"\n{role}")
            self.stdout.write(f"Login: {user.email}")
            self.stdout.write(f"Password: {password}")

from django.core.management.base import BaseCommand
from userauths.models import User  # Import the User model from your userauths app
from store.models import UserProfile

class Command(BaseCommand):
    help = 'Assigns user IDs to UserProfile instances where user_id is None'

    def handle(self, *args, **kwargs):
        users_without_profile = User.objects.filter(profile__isnull=True)

        for user in users_without_profile:
            # Check if the user already has a profile
            if hasattr(user, 'profile'):
                profile = user.profile
            else:
                # If the user doesn't have a profile, create one
                profile = UserProfile.objects.create(user=user)
            self.stdout.write(self.style.SUCCESS(f'Assigned user ID {user.id} to UserProfile {profile.id}'))

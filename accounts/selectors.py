from .models import Profile


def get_profile_for_user(user):
    return Profile.objects.get(user=user)

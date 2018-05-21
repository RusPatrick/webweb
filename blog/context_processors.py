from blog.models import Profile, Tag
from django.core.cache import cache


def add_tags_users_to_context(request):
  if cache.get('top_users') and cache.get('top_tags'):
    print('Data is from cache')
    return cache.get_many(['top_users', 'top_tags'])
  else:
    print('Data is not from cache')
    top_users = Profile.objects.by_rating()[:3]
    top_tags = Tag.objects.hottest()[:3]
    return {'top_users': top_users, 'top_tags': top_tags}

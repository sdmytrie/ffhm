import random
from api.models import Wallpaper


def wallpaper_context_processor(request):
    """Context processor to provide a random wallpaper."""
    all_wallpapers = list(Wallpaper.objects.filter(is_active=True).all())
    wallpaper = random.choice(all_wallpapers) if all_wallpapers else None
    wallpaper_path = f"scoresheet/img/wallpapers/{wallpaper.name}"
    return {"wallpaper_path": wallpaper_path}


def user_agent_context_processor(request):
    user_agent = "default"
    if request.user_agent.is_mobile or request.user_agent.is_tablet:
        user_agent = "mobile"
        if request.user_agent.is_tablet:
            user_agent = "tablet"
    return {"user_agent": user_agent}

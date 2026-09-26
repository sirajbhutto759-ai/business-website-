from .models import ShopSettings

def shop_settings(request):
    try:
        return {'shop_settings': ShopSettings.get_settings()}
    except Exception:
        return {'shop_settings': None}

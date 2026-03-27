from .models import SiteMedia, CarouselImage


def site_media(request):
    media_items = SiteMedia.objects.all()
    return {
        'site_media': {item.slot: item for item in media_items},
        'carousel_images': CarouselImage.objects.all(),
    }

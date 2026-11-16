from urllib.parse import urljoin
from django.urls import reverse


FILTER_QUERY_PARAMS = ("q", "tag", "grade", "major", "lesson", "type", "search")


def _build_abs(base_url: str, path_or_url: str) -> str:
    value = (path_or_url or "").strip()
    if not value:
        return ""
    if value.startswith(("http://", "https://")):
        return value
    return urljoin(f"{base_url.rstrip('/')}/", value.lstrip("/"))


def _safe_field_url(file_field) -> str:
    try:
        if file_field and getattr(file_field, "url", None):
            return file_field.url
    except (ValueError, AttributeError):
        pass
    return ""


def get_site(request):
    site = getattr(request, "site", None)
    configured_base = (getattr(site, "canonical_base_url", "") or "").strip().rstrip("/")
    base_url = configured_base or request.build_absolute_uri("/").rstrip("/")

    canonical_url = f"{base_url}{request.path}"
    page_param = (request.GET.get("page") or "").strip()
    if page_param.isdigit() and int(page_param) > 1:
        canonical_url = f"{canonical_url}?page={int(page_param)}"

    is_filtered = any((request.GET.get(param) or "").strip() for param in FILTER_QUERY_PARAMS)

    logo_fallback = reverse("site:logo")
    logo_path = _safe_field_url(getattr(site, "logo", None)) or logo_fallback
    og_path = (
        _safe_field_url(getattr(site, "og_image", None))
        or _safe_field_url(getattr(site, "about_img", None))
        or logo_path
    )
    apple_icon_path = _safe_field_url(getattr(site, "apple_touch_icon", None)) or logo_path

    return {
        "site": site,
        "seo_base_url": base_url,
        "seo_canonical_url": canonical_url,
        "seo_is_filtered": is_filtered,
        "seo_logo_url": _build_abs(base_url, logo_path),
        "seo_og_image_url": _build_abs(base_url, og_path),
        "seo_apple_touch_icon_url": _build_abs(base_url, apple_icon_path),
    }

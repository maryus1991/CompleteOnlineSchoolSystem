import html
import json
import re
from urllib.parse import urljoin
from django import template
from django.urls import reverse
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def clean_meta(value, max_len=160):
    """Strip HTML tags, normalize whitespace, and truncate cleanly for meta descriptions."""
    if value is None:
        return ""
    text = html.unescape(strip_tags(str(value)))
    text = re.sub(r"\s+", " ", text).strip()
    try:
        limit = int(max_len)
    except (TypeError, ValueError):
        limit = 160
    if limit > 3 and len(text) > limit:
        cut = text[: limit - 1].rsplit(" ", 1)[0].strip()
        if not cut:
            cut = text[: limit - 1].strip()
        return f"{cut}…"
    return text


@register.filter
def schema_iso_date(dt):
    """Convert Jalali or Gregorian datetime objects cleanly to ISO-8601 string."""
    if dt is None:
        return ""
    if hasattr(dt, "togregorian"):
        dt = dt.togregorian()
    if hasattr(dt, "isoformat"):
        return dt.isoformat()
    return str(dt)


@register.simple_tag(takes_context=True)
def abs_url(context, path_or_url):
    value = str(path_or_url or "").strip()
    if not value:
        return ""
    if value.startswith(("http://", "https://")):
        return value
    base_url = (context.get("seo_base_url") or "").strip().rstrip("/")
    if not base_url:
        request = context.get("request")
        if request is not None:
            base_url = request.build_absolute_uri("/").rstrip("/")
    if not base_url:
        return value
    return urljoin(f"{base_url}/", value.lstrip("/"))


def _safe_json_ld(payload) -> str:
    dumped = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    dumped = dumped.replace("</", "<\/")
    return mark_safe(f'<script type="application/ld+json">{dumped}</script>')


def _publisher_dict(site, base_url, logo_url):
    org_type = getattr(site, "organization_type", None) or "EducationalOrganization"
    org = {
        "@type": org_type,
        "@id": f"{base_url}/#organization",
        "name": getattr(site, "name", "") or "",
        "url": f"{base_url}/",
    }
    if logo_url:
        org["logo"] = {
            "@type": "ImageObject",
            "url": logo_url,
        }
    return org


def _page_abs(base_url, path_or_url):
    value = str(path_or_url or "").strip()
    if not value:
        return f"{base_url}/"
    if value.startswith(("http://", "https://")):
        return value
    return urljoin(f"{base_url}/", value.lstrip("/"))


@register.simple_tag(takes_context=True)
def render_global_schemas(context):
    """Emit Organization / EducationalOrganization and WebSite + SearchAction JSON-LD."""
    site = context.get("site")
    if not site:
        return ""
    base_url = (context.get("seo_base_url") or "").rstrip("/")
    logo_url = context.get("seo_logo_url") or ""
    org_type = getattr(site, "organization_type", None) or "EducationalOrganization"

    org_node = {
        "@type": org_type,
        "@id": f"{base_url}/#organization",
        "name": site.name,
        "url": f"{base_url}/",
        "description": clean_meta(site.get_default_description(), 250),
    }
    if logo_url:
        org_node["logo"] = {"@type": "ImageObject", "url": logo_url}
        org_node["image"] = logo_url

    contact_points = []
    if getattr(site, "phone_number_contact", None):
        contact_points.append(
            {
                "@type": "ContactPoint",
                "telephone": str(site.phone_number_contact),
                "contactType": "customer support",
                "availableLanguage": ["fa"],
            }
        )
    if getattr(site, "email_contact", None):
        org_node["email"] = site.email_contact
    if contact_points:
        org_node["contactPoint"] = contact_points

    same_as = site.get_same_as_links() if hasattr(site, "get_same_as_links") else []
    if same_as:
        org_node["sameAs"] = same_as

    search_url = _page_abs(base_url, reverse("article:article-list"))
    website_node = {
        "@type": "WebSite",
        "@id": f"{base_url}/#website",
        "url": f"{base_url}/",
        "name": site.name,
        "inLanguage": "fa-IR",
        "publisher": {"@id": f"{base_url}/#organization"},
        "potentialAction": {
            "@type": "SearchAction",
            "target": {
                "@type": "EntryPoint",
                "urlTemplate": f"{search_url}?q={{search_term_string}}",
            },
            "query-input": "required name=search_term_string",
        },
    }

    return _safe_json_ld(
        {
            "@context": "https://schema.org",
            "@graph": [org_node, website_node],
        }
    )


@register.simple_tag(takes_context=True)
def render_breadcrumb_schema(context, *args):
    """Build BreadcrumbList JSON-LD from pairs of (name, url). Home is prepended automatically."""
    base_url = (context.get("seo_base_url") or "").rstrip("/")
    items = [
        {
            "@type": "ListItem",
            "position": 1,
            "name": "خانه",
            "item": f"{base_url}/",
        }
    ]
    pos = 2
    for i in range(0, len(args) - 1, 2):
        label = clean_meta(args[i], 120)
        url_val = args[i + 1]
        if not label:
            continue
        entry = {
            "@type": "ListItem",
            "position": pos,
            "name": label,
        }
        if url_val:
            entry["item"] = _page_abs(base_url, url_val)
        items.append(entry)
        pos += 1
    return _safe_json_ld(
        {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": items,
        }
    )


@register.simple_tag(takes_context=True)
def render_webpage_schema(context, page_type, title, description=""):
    base_url = (context.get("seo_base_url") or "").rstrip("/")
    canonical = context.get("seo_canonical_url") or f"{base_url}/"
    payload = {
        "@context": "https://schema.org",
        "@type": page_type or "WebPage",
        "@id": f"{canonical}#webpage",
        "url": canonical,
        "name": clean_meta(title, 140),
        "inLanguage": "fa-IR",
        "isPartOf": {"@id": f"{base_url}/#website"},
    }
    if description:
        payload["description"] = clean_meta(description, 250)
    return _safe_json_ld(payload)


@register.simple_tag(takes_context=True)
def render_faq_schema(context, items):
    entities = []
    for faq in items or []:
        q = clean_meta(getattr(faq, "question", ""), 300)
        a = clean_meta(getattr(faq, "answer", ""), 2000)
        if q and a:
            entities.append(
                {
                    "@type": "Question",
                    "name": q,
                    "acceptedAnswer": {
                        "@type": "Answer",
                        "text": a,
                    },
                }
            )
    if not entities:
        return ""
    return _safe_json_ld(
        {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": entities,
        }
    )


@register.simple_tag(takes_context=True)
def render_article_schema(context, article, rating_avg=0, rating_count=0):
    site = context.get("site")
    base_url = (context.get("seo_base_url") or "").rstrip("/")
    logo_url = context.get("seo_logo_url") or ""
    canonical = context.get("seo_canonical_url") or _page_abs(base_url, article.get_absolute_url())

    image_url = context.get("seo_og_image_url") or ""
    try:
        if getattr(article, "image", None) and article.image.url:
            image_url = _page_abs(base_url, article.image.url)
    except (ValueError, AttributeError):
        pass

    author_name = ""
    if getattr(article, "user", None):
        author_name = article.user.get_full_name() or getattr(article.user, "username", "") or getattr(site, "name", "")

    keywords = [t.name for t in article.tags.all() if getattr(t, "name", None)]

    payload = {
        "@context": "https://schema.org",
        "@type": "Article",
        "mainEntityOfPage": {
            "@type": "WebPage",
            "@id": canonical,
        },
        "headline": clean_meta(article.name, 110),
        "description": clean_meta(article.summery or article.text, 200),
        "inLanguage": "fa-IR",
        "datePublished": schema_iso_date(article.created_at),
        "dateModified": schema_iso_date(article.updated_at),
        "publisher": _publisher_dict(site, base_url, logo_url),
        "author": {
            "@type": "Person",
            "name": author_name or (site.name if site else ""),
        },
    }
    if image_url:
        payload["image"] = [image_url]
    if getattr(article, "category", None):
        payload["articleSection"] = article.category.name
    if keywords:
        payload["keywords"] = ", ".join(keywords)
    if getattr(article, "reading_time", None):
        payload["timeRequired"] = f"PT{int(article.reading_time)}M"
    try:
        total_ratings = int(rating_count or 0)
        avg_val = float(rating_avg or 0)
        if total_ratings > 0 and avg_val > 0:
            payload["aggregateRating"] = {
                "@type": "AggregateRating",
                "ratingValue": round(avg_val, 1),
                "bestRating": 5,
                "worstRating": 1,
                "ratingCount": total_ratings,
            }
    except (TypeError, ValueError):
        pass

    return _safe_json_ld(payload)


@register.simple_tag(takes_context=True)
def render_course_schema(context, course):
    site = context.get("site")
    base_url = (context.get("seo_base_url") or "").rstrip("/")
    logo_url = context.get("seo_logo_url") or ""
    canonical = context.get("seo_canonical_url") or _page_abs(base_url, course.get_absolute_url())
    currency = getattr(site, "price_currency", None) or "IRR"

    image_url = context.get("seo_og_image_url") or ""
    try:
        if getattr(course, "image", None) and course.image.url:
            image_url = _page_abs(base_url, course.image.url)
    except (ValueError, AttributeError):
        pass

    price_val = 0 if getattr(course, "is_free", False) else int(getattr(course, "price", 0) or 0)

    payload = {
        "@context": "https://schema.org",
        "@type": "Course",
        "name": clean_meta(course.name, 140),
        "description": clean_meta(course.summery or course.text, 300),
        "url": canonical,
        "inLanguage": "fa-IR",
        "provider": _publisher_dict(site, base_url, logo_url),
        "offers": {
            "@type": "Offer",
            "price": price_val,
            "priceCurrency": currency,
            "availability": "https://schema.org/InStock",
            "category": "Free" if price_val == 0 else "Paid",
        },
    }
    if image_url:
        payload["image"] = image_url
    if getattr(course, "teacher", None) and getattr(course.teacher, "user", None):
        instructor_name = course.teacher.user.get_full_name()
        if instructor_name:
            payload["hasCourseInstance"] = {
                "@type": "CourseInstance",
                "courseMode": "online",
                "instructor": {
                    "@type": "Person",
                    "name": instructor_name,
                },
            }
    if getattr(course, "grade", None):
        payload["educationalLevel"] = course.grade.name
    if getattr(course, "lesson", None):
        payload["teaches"] = course.lesson.name

    return _safe_json_ld(payload)


@register.simple_tag(takes_context=True)
def render_exam_schema(context, exam):
    site = context.get("site")
    base_url = (context.get("seo_base_url") or "").rstrip("/")
    logo_url = context.get("seo_logo_url") or ""
    canonical = context.get("seo_canonical_url") or _page_abs(base_url, exam.get_absolute_url())
    currency = getattr(site, "price_currency", None) or "IRR"

    image_url = context.get("seo_og_image_url") or ""
    try:
        if getattr(exam, "image", None) and exam.image.url:
            image_url = _page_abs(base_url, exam.image.url)
    except (ValueError, AttributeError):
        pass

    price_val = 0 if getattr(exam, "is_free", False) else int(getattr(exam, "price", 0) or 0)

    payload = {
        "@context": "https://schema.org",
        "@type": "LearningResource",
        "learningResourceType": "Quiz",
        "name": clean_meta(exam.name, 140),
        "description": clean_meta(exam.summery or exam.description or exam.section or exam.name, 300),
        "url": canonical,
        "inLanguage": "fa-IR",
        "provider": _publisher_dict(site, base_url, logo_url),
        "isAccessibleForFree": price_val == 0,
        "offers": {
            "@type": "Offer",
            "price": price_val,
            "priceCurrency": currency,
            "availability": "https://schema.org/InStock",
        },
    }
    if image_url:
        payload["image"] = image_url
    if getattr(exam, "time_minutes", None):
        payload["timeRequired"] = f"PT{int(exam.time_minutes)}M"
    if getattr(exam, "grade", None):
        payload["educationalLevel"] = exam.grade.name
    if getattr(exam, "lesson", None):
        payload["assesses"] = exam.lesson.name

    return _safe_json_ld(payload)


@register.simple_tag(takes_context=True)
def render_qbank_schema(context, question):
    base_url = (context.get("seo_base_url") or "").rstrip("/")
    canonical = context.get("seo_canonical_url") or _page_abs(base_url, question.get_absolute_url())

    q_text = clean_meta(question.description or question.name, 1000)
    correct_text = ""
    try:
        correct_opts = [opt.name for opt in question.options.filter(is_correct=True)]
        if correct_opts:
            correct_text = "، ".join(clean_meta(o, 250) for o in correct_opts)
    except Exception:
        pass

    main_entity = {
        "@type": "Question",
        "name": clean_meta(question.name, 200),
        "text": q_text,
        "dateCreated": schema_iso_date(question.created_at),
    }
    if correct_text:
        main_entity["acceptedAnswer"] = {
            "@type": "Answer",
            "text": f"پاسخ صحیح: {correct_text}",
        }

    return _safe_json_ld(
        {
            "@context": "https://schema.org",
            "@type": "QAPage",
            "url": canonical,
            "inLanguage": "fa-IR",
            "mainEntity": main_entity,
        }
    )

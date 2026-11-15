from typing import Any

from django.http import HttpRequest, HttpResponseBase
from django.shortcuts import redirect
from django.views.generic import TemplateView, CreateView, ListView
from django.contrib import messages
from apps.sitesetting.forms import ContactForm, CounselingForm
from django.urls import reverse_lazy

from apps.sitesetting.models import FAQ, TimeLine, TestMonomials
from apps.classes.models import Class
from apps.users.accounts.models import User
from apps.article.models import Article
from django.db.models import Count, Exists, OuterRef
from apps.users.students.models import Student



from django.http import FileResponse, HttpResponse
from django.core.exceptions import ObjectDoesNotExist


def logo(request):
    try:
        logo_file = request.site.logo

        if logo_file:
            return FileResponse(
                logo_file.open("rb"),
                content_type="image/png",
            )

    except (AttributeError, ValueError, ObjectDoesNotExist, OSError):
        pass

    return HttpResponse(
        """
             <svg xmlns="http://www.w3.org/2000/svg"
                 viewBox="-50 -50 1300 1100"
                 width="50" height="50"
                 fill="none">
            
              <defs>
                <!-- Deep space background gradient -->
                <radialGradient id="bg" cx="600" cy="500" r="750"
                                gradientUnits="userSpaceOnUse">
                  <stop offset="0"   stop-color="#0F2149"/>
                  <stop offset="0.6" stop-color="#091533"/>
                  <stop offset="1"   stop-color="#040C1E"/>
                </radialGradient>
            
                <!-- White-silver metallic gradient -->
                <linearGradient id="silver" x1="300" y1="180" x2="900" y2="820"
                                gradientUnits="userSpaceOnUse">
                  <stop offset="0"    stop-color="#FFFFFF"/>
                  <stop offset="0.25" stop-color="#F4F6FC"/>
                  <stop offset="0.55" stop-color="#E4E9F4"/>
                  <stop offset="0.8"  stop-color="#CBD4EA"/>
                  <stop offset="1"    stop-color="#B0BDD8"/>
                </linearGradient>
            
                <!-- Rich gold gradient -->
                <linearGradient id="gold" x1="85" y1="925" x2="1100" y2="260"
                                gradientUnits="userSpaceOnUse">
                  <stop offset="0"    stop-color="#A0600A"/>
                  <stop offset="0.15" stop-color="#C87916"/>
                  <stop offset="0.35" stop-color="#FFB323"/>
                  <stop offset="0.55" stop-color="#FFCC44"/>
                  <stop offset="0.75" stop-color="#FFE477"/>
                  <stop offset="0.9"  stop-color="#FFF0A0"/>
                  <stop offset="1"    stop-color="#FFFACC"/>
                </linearGradient>
            
                <!-- Star gradient -->
                <radialGradient id="starGrad" cx="1062" cy="225" r="160"
                                gradientUnits="userSpaceOnUse">
                  <stop offset="0"   stop-color="#FFFEF0"/>
                  <stop offset="0.3" stop-color="#FFE87A"/>
                  <stop offset="0.6" stop-color="#FFD34D"/>
                  <stop offset="1"   stop-color="#D99018"/>
                </radialGradient>
            
                <!-- Rim light for the letter -->
                <linearGradient id="rim" x1="400" y1="195" x2="800" y2="790"
                                gradientUnits="userSpaceOnUse">
                  <stop offset="0"   stop-color="#A8C4FF" stop-opacity="0.9"/>
                  <stop offset="0.5" stop-color="#7DA8E8" stop-opacity="0.5"/>
                  <stop offset="1"   stop-color="#5B7DB8" stop-opacity="0.3"/>
                </linearGradient>
            
                <!-- Drop shadow for the letter -->
                <filter id="dropShadow" x="-15%" y="-15%" width="135%" height="135%">
                  <feDropShadow dx="6" dy="10" stdDeviation="12"
                                flood-color="#020B1E" flood-opacity="0.55"/>
                </filter>
            
                <!-- Soft glow for the swoosh -->
                <filter id="swooshGlow" x="-10%" y="-30%" width="120%" height="160%">
                  <feGaussianBlur in="SourceGraphic" stdDeviation="8" result="blur"/>
                  <feColorMatrix in="blur" type="matrix"
                    values="1 0 0 0 0.1
                            0 0.8 0 0 0.05
                            0 0 0.2 0 0
                            0 0 0 0.5 0" result="glow"/>
                  <feMerge>
                    <feMergeNode in="glow"/>
                    <feMergeNode in="SourceGraphic"/>
                  </feMerge>
                </filter>
            
                <!-- Star glow -->
                <filter id="starGlow" x="-50%" y="-50%" width="200%" height="200%">
                  <feGaussianBlur in="SourceGraphic" stdDeviation="10" result="blur"/>
                  <feColorMatrix in="blur" type="matrix"
                    values="1 0 0 0 0.2
                            0 0.9 0 0 0.1
                            0 0 0.3 0 0
                            0 0 0 0.7 0" result="glow"/>
                  <feMerge>
                    <feMergeNode in="glow"/>
                    <feMergeNode in="SourceGraphic"/>
                  </feMerge>
                </filter>
            
                <!-- Subtle inner bevel for the A -->
                <filter id="bevel" x="-5%" y="-5%" width="110%" height="110%">
                  <feGaussianBlur in="SourceAlpha" stdDeviation="3" result="blur"/>
                  <feSpecularLighting in="blur" surfaceScale="4" specularConstant="0.6"
                                      specularExponent="25" result="spec"
                                      lighting-color="#FFFFFF">
                    <fePointLight x="450" y="150" z="300"/>
                  </feSpecularLighting>
                  <feComposite in="spec" in2="SourceAlpha" operator="in" result="specOut"/>
                  <feMerge>
                    <feMergeNode in="SourceGraphic"/>
                    <feMergeNode in="specOut"/>
                  </feMerge>
                </filter>
              </defs>
            
              <!-- Background -->
              <rect x="-50" y="-50" width="1300" height="1100" rx="60" fill="url(#bg)"/>
            
              <!-- Subtle background stars / dust -->
              <circle cx="120" cy="80" r="1.5" fill="#ffffff" opacity="0.3"/>
              <circle cx="300" cy="40" r="1"   fill="#ffffff" opacity="0.25"/>
              <circle cx="750" cy="60" r="1.2" fill="#ffffff" opacity="0.2"/>
              <circle cx="200" cy="950" r="1"  fill="#ffffff" opacity="0.15"/>
              <circle cx="950" cy="900" r="1.3" fill="#ffffff" opacity="0.2"/>
              <circle cx="50"  cy="500" r="1"  fill="#ffffff" opacity="0.18"/>
              <circle cx="1150" cy="600" r="1.5" fill="#ffffff" opacity="0.22"/>
              <circle cx="850" cy="950" r="1"  fill="#ffffff" opacity="0.15"/>
              <circle cx="500" cy="920" r="0.8" fill="#ffffff" opacity="0.2"/>
              <circle cx="1100" cy="800" r="1.2" fill="#ffffff" opacity="0.18"/>
            
              <!-- ===== LETTER A ===== -->
              <g filter="url(#dropShadow)">
                <!-- Main letter A — left leg + peak + crossbar -->
                <path d="
                  M175 790
                  L500 310
                  L560 220
                  Q575 195 605 195
                  L690 195
                  Q720 195 738 220
                  L825 340
                  L755 390
                  L680 285
                  L620 370
                  L450 620
                  L365 680
                  Z"
                  fill="url(#silver)"
                  filter="url(#bevel)"/>
            
                <!-- Right leg of A -->
                <path d="
                  M755 460
                  L825 420
                  L1050 780
                  L920 780
                  Z"
                  fill="url(#silver)"
                  filter="url(#bevel)"/>
              </g>
            
              <!-- Rim / edge light on the letter -->
              <path d="
                M175 790
                L500 310
                L560 220
                Q575 195 605 195
                L690 195
                Q720 195 738 220
                L825 340
                L755 390
                L680 285
                L620 370
                L450 620
                L365 680
                Z"
                fill="none"
                stroke="url(#rim)"
                stroke-width="3"
                stroke-linejoin="round"/>
            
              <path d="
                M755 460
                L825 420
                L1050 780
                L920 780
                Z"
                fill="none"
                stroke="url(#rim)"
                stroke-width="3"
                stroke-linejoin="round"/>
            
              <!-- ===== GOLD COMET SWOOSH ===== -->
              <g filter="url(#swooshGlow)">
                <path d="
                  M85 925
                  C205 765 380 610 560 500
                  C730 395 900 320 1100 260
                  C920 330 755 405 610 500
                  C445 605 320 740 270 840
                  C205 865 140 900 85 925
                  Z"
                  fill="url(#gold)"/>
              </g>
            
              <!-- Swoosh top highlight -->
              <path d="
                M100 915
                C300 690 550 520 820 385
                C925 335 1010 300 1100 260"
                stroke="#FFF6C8"
                stroke-width="4"
                stroke-linecap="round"
                opacity="0.85"/>
            
              <!-- Swoosh bottom subtle edge -->
              <path d="
                M85 925
                C205 765 380 610 560 500
                C730 395 900 320 1100 260"
                stroke="#A06010"
                stroke-width="2"
                stroke-linecap="round"
                opacity="0.3"
                transform="translate(0 8)"/>
            
              <!-- ===== FOUR-POINT STAR ===== -->
              <g filter="url(#starGlow)">
                <path d="
                  M1060 65
                  C1070 165 1078 190 1100 205
                  C1130 220 1170 220 1190 225
                  C1140 235 1110 245 1100 270
                  C1085 300 1080 345 1075 375
                  C1065 300 1055 260 1030 245
                  C1000 230 970 230 935 225
                  C1000 215 1035 205 1045 180
                  C1055 150 1058 105 1060 65
                  Z"
                  fill="url(#starGrad)"/>
              </g>
            
              <!-- Star center core -->
              <path d="
                M1060 145
                L1072 215
                L1140 225
                L1072 237
                L1060 305
                L1048 237
                L980 225
                L1048 215
                Z"
                fill="#FFFEF2"
                opacity="0.85"/>
            
              <!-- Tiny sparkle dots near the star -->
              <circle cx="970"  cy="140" r="2.5" fill="#FFE477" opacity="0.5"/>
              <circle cx="1150" cy="150" r="2"   fill="#FFE477" opacity="0.4"/>
              <circle cx="1130" cy="350" r="1.8" fill="#FFD34D" opacity="0.35"/>
            
            </svg>
        """,
        content_type="image/svg+xml",
    )

class Main(TemplateView):
    template_name = 'main/index.html'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)


        data.update(
            {
                "course": Class.objects.filter(
                        is_active=True,
                        teacher__is_active=True,
                        lesson__is_active=True,
                        major__is_active=True,
                        grade__is_active=True,
                        is_public=True,
                    ).annotate(
                        student_count=Count('student', distinct=True),
                        section_count=Count('sections', distinct=True),
                        is_student=Exists(
                            Student.objects.filter(
                                user=self.request.user if self.request.user.is_authenticated else None,
                                classes=OuterRef("pk"),
                            )
                        ),
                    ).select_related("grade", "major", "lesson").prefetch_related("sections").distinct()[:3],
                "mentors": User.objects.filter(is_active=True, publish=True).all()[:3],
                "blog": Article.objects.filter(is_active=True).select_related("category").all()[:3],
            }
        )

        return data

class About(TemplateView):
    template_name = 'main/site/about.html'

    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponseBase:
        if not request.site.about_active:
            messages.error(request, "این صفحه غیر فعال میباشد")
            return redirect("site:main")
        return super().dispatch(request, *args, **kwargs)


    def get_context_data(self, **kwargs: Any) -> dict:
        data = super().get_context_data(**kwargs)

        data.update(
            {
                "timeline": TimeLine.objects.filter(is_active=True).all(),
                "testimonials": TestMonomials.objects.filter(is_active=True).all(),
            }
        )

        return data

class FAQListView(ListView):
    """for list faqs"""

    template_name = 'main/site/faq.html'
    queryset = FAQ.objects.filter(is_active=True).all()
    context_object_name = 'items'

    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponseBase:
        if not request.site.faq_active:
            messages.error(request, "این صفحه غیر فعال میباشد")
            return redirect("site:main")
        return super().dispatch(request, *args, **kwargs)

class Contact(CreateView):
    template_name = 'main/site/contact.html'
    form_class = ContactForm
    success_url = reverse_lazy('site:contact')

    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponseBase:
        if not request.site.active_contact:
            messages.error(request, "این صفحه غیر فعال میباشد")
            return redirect("site:main")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, "پیام شما ارسال شد")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.success(self.request, form.errors, fail_silently=True)
        return super().form_invalid(form)

class Counseling(CreateView):
    template_name = 'main/site/free-counseling.html'
    form_class = CounselingForm
    success_url = reverse_lazy('site:counseling')

    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponseBase:
        if not request.site.active_counseling:
            messages.error(request, "این صفحه غیر فعال میباشد")
            return redirect("site:main")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, "پیام شما ارسال شد")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.success(self.request, form.errors, fail_silently=True)
        return super().form_invalid(form)
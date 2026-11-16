from django import forms
from .models import ArticleComment


class ArticleRatingForm(forms.Form):
    score = forms.IntegerField(min_value=1, max_value=5, required=True)


class ArticleCommentForm(forms.ModelForm):
    parent_id = forms.IntegerField(required=False, widget=forms.HiddenInput())

    class Meta:
        model = ArticleComment
        fields = ["text"]
        widgets = {
            "text": forms.Textarea(
                attrs={
                    "rows": 4,
                    "maxlength": 1500,
                    "placeholder": "دیدگاه یا سوال خود را درباره این مقاله بنویسید...",
                    "class": "comment-textarea",
                }
            )
        }

    def clean_text(self):
        text = (self.cleaned_data.get("text") or "").strip()
        if len(text) < 3:
            raise forms.ValidationError("متن دیدگاه باید حداقل ۳ کاراکتر باشد.")
        return text

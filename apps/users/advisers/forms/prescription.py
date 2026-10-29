from django import forms
from apps.progress.models import AdviserExamPrescription


class AdviserExamPrescriptionForm(forms.ModelForm):
    class Meta:
        model = AdviserExamPrescription
        fields = [
            "strengths_analysis",
            "weaknesses_analysis",
            "action_plan_for_next_exam",
            "voice_or_file_attachment",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["voice_or_file_attachment"].required = False

from dateutil.relativedelta import relativedelta
from django import forms
from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist
from edc_form_validators import FormValidator


class SubjectConsentFormValidator(FormValidator):

    subject_screening_model = "meta_screening.subjectscreening"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if "dob" not in self.cleaned_data:
            self.dob = self.instance.dob
        else:
            self.dob = self.cleaned_data.get("dob")
        if "consent_datetime" not in self.cleaned_data:
            self.consent_datetime = self.instance.consent_datetime
        else:
            self.consent_datetime = self.cleaned_data.get("consent_datetime")
        self.guardian_name = self.cleaned_data.get("guardian_name")
        if "screening_identifier" not in self.cleaned_data:
            self.screening_identifier = self.instance.dobscreening_identifier
        else:
            self.screening_identifier = self.cleaned_data.get("screening_identifier")

    @property
    def subject_screening_model_cls(self):
        return django_apps.get_model(self.subject_screening_model)

    def clean(self):
        try:
            subject_screening = self.subject_screening_model_cls.objects.get(
                screening_identifier=self.screening_identifier
            )
        except ObjectDoesNotExist:
            raise forms.ValidationError(
                'Complete the "Subject Screening" form before proceeding.',
                code="missing_subject_screening",
            )

        if self.add_form and not self.consent_datetime:
            raise forms.ValidationError({"consent_datetime": "This field is required."})

        screening_age_in_years = relativedelta(
            subject_screening.report_datetime.date(), self.dob
        ).years
        if screening_age_in_years != subject_screening.age_in_years:
            raise forms.ValidationError(
                {
                    "dob": "Age mismatch. The date of birth entered does "
                    f"not match the age at screening. "
                    f"Expected {subject_screening.age_in_years}. "
                    f"Got {screening_age_in_years}."
                }
            )
        if (
            self.consent_datetime - subject_screening.eligibility_datetime
        ).total_seconds() <= 0:
            raise forms.ValidationError(
                {"consent_datetime": "Cannot be before the screening datetime."}
            )
        if self.cleaned_data.get("identity_type") != "hospital_no":
            raise forms.ValidationError(
                {"identity_type": "Expected 'hospital number'."}
            )

        if subject_screening.hospital_identifier != self.cleaned_data.get("identity"):
            raise forms.ValidationError(
                {
                    "identity": (
                        "The hospital identifier does not match that "
                        "reported at screening."
                    )
                }
            )

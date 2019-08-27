from edc_constants.constants import FEMALE, MALE
from edc_constants.constants import YES
from edc_form_validators import FormValidator
from edc_reportable import NormalReference
from edc_reportable.units import MICROMOLES_PER_LITER


gluc_fasting_ref = NormalReference(
    name="gluc",
    lower=6.1,
    upper=6.9,
    lower_inclusive=True,
    upper_inclusive=True,
    units=MICROMOLES_PER_LITER,
    gender=[MALE, FEMALE],
    age_lower=18,
    age_lower_inclusive=True,
)

gluc_2hr_ref = NormalReference(
    name="gluc_2hr",
    lower=7.00,
    upper=11.10,
    lower_inclusive=True,
    upper_inclusive=True,
    units=MICROMOLES_PER_LITER,
    gender=[MALE, FEMALE],
    age_lower=18,
    age_lower_inclusive=True,
)


class SubjectScreeningFormValidator(FormValidator):

    def clean(self):

        opt = dict(
            name="gluc",
            lower_inclusive=True,
            upper_inclusive=True,
            units=MICROMOLES_PER_LITER,
            gender=[MALE, FEMALE],
            age_lower=18,
            age_lower_inclusive=True,
        )

        if self.cleaned_data.get("bmi") > 30:
            gluc_ref = NormalReference(lower=6.1, upper=6.9, **opt)

        self.required_if(YES, field="bmi", field_required="glucose_fasting")

        self.required_if(YES, field="bmi", field_required="glucose_two_hours")

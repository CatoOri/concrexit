import datetime

from django.conf import settings
from django.forms import (ChoiceField, DateField, ModelChoiceField,
                          ModelForm, SelectDateWidget,
                          TypedChoiceField)
from django.utils import timezone

from utils.snippets import datetime_to_lectureyear
from .models import Course, Exam, Summary


class AddExamForm(ModelForm):
    this_year = datetime.date.today().year
    years = list(reversed(range(this_year - 8, this_year + 1)))

    exam_date = DateField(
        widget=SelectDateWidget(years=years),
        initial=datetime.date.today
    )
    course = ModelChoiceField(
        queryset=Course.objects.order_by('name_' + settings.LANGUAGE_CODE),
        empty_label=None)
    type = ChoiceField(choices=Exam.EXAM_TYPES)

    class Meta:
        model = Exam
        fields = ('file', 'course', 'type', 'exam_date')


class AddSummaryForm(ModelForm):
    course = ModelChoiceField(
        queryset=Course.objects.order_by('name_' + settings.LANGUAGE_CODE),
        empty_label=None)

    this_year = datetime_to_lectureyear(timezone.now())
    years = reversed([(x, "{} - {}".format(x, x + 1)) for x in
                      range(this_year - 20, this_year + 1)])

    year = TypedChoiceField(choices=years, coerce=int, empty_value=this_year)

    class Meta:
        model = Summary
        fields = ('name', 'year', 'file', 'course', 'author')

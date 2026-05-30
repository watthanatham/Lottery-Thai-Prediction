from django import forms
from .models import LotteryDraw, AnalysisSession


class LotteryDrawForm(forms.ModelForm):
    class Meta:
        model = LotteryDraw
        fields = [
            'draw_date', 'first_prize',
            'near_first_1', 'near_first_2',
            'three_front_1', 'three_front_2',
            'three_back_1', 'three_back_2',
            'two_back', 'notes',
        ]
        widgets = {
            'draw_date': forms.DateInput(
                attrs={'type': 'date', 'class': 'form-control'}, format='%Y-%m-%d'),
            'first_prize': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': '123456', 'maxlength': 6}),
            'near_first_1': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Auto', 'maxlength': 6}),
            'near_first_2': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Auto', 'maxlength': 6}),
            'three_front_1': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Auto', 'maxlength': 3}),
            'three_front_2': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': '---', 'maxlength': 3}),
            'three_back_1': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Auto', 'maxlength': 3}),
            'three_back_2': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': '---', 'maxlength': 3}),
            'two_back': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Auto', 'maxlength': 2}),
            'notes': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Optional notes…'}),
        }

    def clean_first_prize(self):
        fp = self.cleaned_data.get('first_prize', '').strip()
        if not fp.isdigit() or len(fp) != 6:
            raise forms.ValidationError("First prize must be exactly 6 digits.")
        return fp


class AnalysisRunForm(forms.Form):
    LOTTERY_TYPE_CHOICES = [
        ('2D', '2-Digit Back (เลขท้าย 2 ตัว)'),
        ('3F', '3-Digit Front (เลขหน้า 3 ตัว)'),
        ('3B', '3-Digit Back (เลขหลัง 3 ตัว)'),
    ]
    lottery_type = forms.ChoiceField(
        choices=LOTTERY_TYPE_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'btn-check'}),
        initial='2D',
        label='Lottery Type',
    )
    history_limit = forms.IntegerField(
        min_value=5, max_value=200, initial=50,
        label='Draws to include in analysis',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'style': 'width:6rem'}),
    )
    target_draw_date = forms.DateField(
        required=False,
        label='Target Draw Date (optional)',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}, format='%Y-%m-%d'),
    )


class FormulaWeightForm(forms.Form):
    """Dynamically built — one row per FormulaConfig."""
    pass

from django import forms
from django.utils import timezone
from .models import Attendance, LeaveRequest

class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['user','date','check_in','check_out','status','notes']
        widgets = {
            'date': forms.DateInput(attrs={'type':'date','class':'form-control'}),
            'check_in': forms.TimeInput(attrs={'type':'time','class':'form-control'}),
            'check_out': forms.TimeInput(attrs={'type':'time','class':'form-control'}),
            'notes': forms.Textarea(attrs={'rows':2,'class':'form-control'}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, f in self.fields.items():
            if not f.widget.attrs.get('class'):
                f.widget.attrs['class'] = 'form-control'

class CheckInForm(forms.Form):
    notes = forms.CharField(widget=forms.Textarea(attrs={'rows':2,'class':'form-control','placeholder':'Optional notes...'}), required=False)

class LeaveRequestForm(forms.ModelForm):
    class Meta:
        model = LeaveRequest
        fields = ['leave_type','start_date','end_date','reason']
        widgets = {
            'start_date': forms.DateInput(attrs={'type':'date','class':'form-control'}),
            'end_date': forms.DateInput(attrs={'type':'date','class':'form-control'}),
            'reason': forms.Textarea(attrs={'rows':3,'class':'form-control'}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, f in self.fields.items():
            if not f.widget.attrs.get('class'):
                f.widget.attrs['class'] = 'form-control'
    def clean(self):
        cleaned = super().clean()
        start = cleaned.get('start_date')
        end = cleaned.get('end_date')
        if start and end and end < start:
            raise forms.ValidationError('End date cannot be before start date.')
        return cleaned

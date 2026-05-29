from django import forms
from .models import Task, TaskComment
from accounts.models import User

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title','description','assigned_to','priority','status','due_date','tags']
        widgets = {
            'due_date': forms.DateInput(attrs={'type':'date','class':'form-control'}),
            'description': forms.Textarea(attrs={'rows':4,'class':'form-control'}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['assigned_to'].queryset = User.objects.filter(is_active=True)
        for name, f in self.fields.items():
            if not f.widget.attrs.get('class'):
                f.widget.attrs['class'] = 'form-control'

class TaskCommentForm(forms.ModelForm):
    class Meta:
        model = TaskComment
        fields = ['content']
        widgets = {'content': forms.Textarea(attrs={'rows':3,'class':'form-control','placeholder':'Add a comment...'})}

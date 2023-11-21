# forms.py
from django import forms
from .models import File,Comment

class FileForm(forms.ModelForm):
    class Meta:
        model = File
        fields = ['subject', 'content', 'file']  # 여기서 'file'은 사용자가 업로드할 파일 필드
        
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        labels = {
            'content': '답변내용',
        }

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator

# File 모델
class File(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='authored_files')         # 작성자
    subject = models.CharField(max_length=255)                          # 제목
    content = models.TextField(null=True,default='')                    # 내용
    file = models.FileField(                                    # 파일 필드로 변경
        upload_to='uploads/pdfs/',                              # 파일 업로드 경로 설정
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])]  # PDF 파일만 허용
    )
    likes = models.IntegerField(default=0)                              # 좋아요 수, 기본값 0
    create_date = models.DateTimeField(null=True,default='' )           # 생성 날짜
    modify_date = models.DateTimeField(null=True,blank=True)            # 수정 날짜
    voter = models.ManyToManyField(User, related_name='voted_files')  # 추천인 추가

# Comment 모델
class Comment(models.Model):
    file = models.ForeignKey(File, on_delete=models.CASCADE)            # File 모델의 외래키
    author = models.ForeignKey(User, on_delete=models.CASCADE)                     # 댓글 작성자
    content = models.TextField(null=True,default='')                         # 댓글 내용
    creation_date = models.DateTimeField(null=True,default='')          # 댓글 작성일
    modify_date = models.DateTimeField(null=True, blank=True)


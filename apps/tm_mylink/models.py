from django.db import models
from django.contrib.auth import get_user_model

# Create your models here.
class inquiry_db(models.Model) :
    author = models.ForeignKey(
        get_user_model(),
        on_delete = models.CASCADE,
        related_name = 'inq_user',
        verbose_name = '작성자'
    )

    user_title = models.CharField('제목', max_length=100)
    user_content = models.TextField('내용')
    userinquiry_at = models.DateTimeField('작성일', auto_now_add=True)

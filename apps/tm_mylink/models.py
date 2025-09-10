from django.db import models

# Create your models here.
class inquiry_db(models.Model) :
    user_title = models.CharField('제목', max_length=100)
    user_content = models.TextField('내용')
    userinquiry_at = models.TimeField('작성일',auto_now=True)
    class Meta:
        app_label = 'tm_mylink'
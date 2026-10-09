from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0006_articleview_alter_articlelike_unique_together_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='cover_logo',
            field=models.ImageField(
                blank=True, null=True, upload_to='projects/logos/', verbose_name='Логотип для обложки',
                help_text='Если главного изображения нет, карточка рисует обложку сама; с логотипом он стоит на плитке вместо значка',
            ),
        ),
    ]

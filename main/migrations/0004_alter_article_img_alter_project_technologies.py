from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_article_extensions'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='img',
            field=models.ImageField(blank=True, null=True, upload_to='articles/', verbose_name='Превью (обложка)'),
        ),
        migrations.AlterField(
            model_name='project',
            name='technologies',
            field=models.CharField(help_text='Например: Django, React, PostgreSQL', max_length=500, verbose_name='Технологии (через запятую)'),
        ),
    ]

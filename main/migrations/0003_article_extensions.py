from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('main', '0002_sitesettings_alter_category_options_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProjectStatus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='Название')),
                ('slug', models.SlugField(max_length=50, unique=True, verbose_name='Код')),
                ('color', models.CharField(default='primary', max_length=20, verbose_name='Цвет (CSS класс)')),
                ('is_release',
                 models.BooleanField(default=False, help_text='Проекты с этим статусом попадают в "Завершённые"',
                                     verbose_name='Это релиз')),
                ('order', models.PositiveIntegerField(default=0, verbose_name='Порядок')),
            ],
            options={
                'verbose_name': 'Статус проекта',
                'verbose_name_plural': 'Статусы проектов',
                'ordering': ['order'],
            },
        ),

        migrations.CreateModel(
            name='ArticleImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='articles/gallery/', verbose_name='Изображение')),
                ('caption', models.CharField(blank=True, max_length=255, verbose_name='Подпись')),
                ('order', models.PositiveIntegerField(default=0, verbose_name='Порядок')),
                ('is_inline',
                 models.BooleanField(default=False, help_text='Отметьте, если это изображение вставлено в текст статьи',
                                     verbose_name='Добавлено через редактор')),
                ('article',
                 models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='gallery_images',
                                   to='main.article', verbose_name='Статья')),
            ],
            options={
                'verbose_name': 'Изображение статьи',
                'verbose_name_plural': 'Изображения статьи',
                'ordering': ['order'],
            },
        ),

        migrations.CreateModel(
            name='ArticleFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='articles/files/', verbose_name='Файл')),
                ('title', models.CharField(max_length=255, verbose_name='Название файла')),
                ('description', models.TextField(blank=True, verbose_name='Описание')),
                ('order', models.PositiveIntegerField(default=0, verbose_name='Порядок')),
                ('is_inline', models.BooleanField(default=False,
                                                  help_text='Отметьте, если ссылка на этот файл вставлена в текст статьи',
                                                  verbose_name='Добавлено через редактор')),
                ('article',
                 models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attached_files',
                                   to='main.article', verbose_name='Статья')),
            ],
            options={
                'verbose_name': 'Файл статьи',
                'verbose_name_plural': 'Файлы статьи',
                'ordering': ['order'],
            },
        ),

        migrations.CreateModel(
            name='ArticleLink',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.URLField(verbose_name='URL')),
                ('title', models.CharField(blank=True, max_length=255, verbose_name='Заголовок')),
                ('description', models.TextField(blank=True, verbose_name='Описание')),
                ('preview_image', models.URLField(blank=True, verbose_name='URL изображения превью')),
                ('order', models.PositiveIntegerField(default=0, verbose_name='Порядок')),
                ('is_inline',
                 models.BooleanField(default=False, help_text='Отметьте, если эта ссылка вставлена в текст статьи',
                                     verbose_name='Добавлено через редактор')),
                ('article',
                 models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attached_links',
                                   to='main.article', verbose_name='Статья')),
            ],
            options={
                'verbose_name': 'Ссылка статьи',
                'verbose_name_plural': 'Ссылки статьи',
                'ordering': ['order'],
            },
        ),
        migrations.AddField(
            model_name='article',
            name='comments_enabled',
            field=models.BooleanField(default=True, verbose_name='Включить комментарии'),
        ),
        migrations.AddField(
            model_name='article',
            name='show_cover_in_article',
            field=models.BooleanField(default=True, verbose_name='Показывать обложку в начале статьи'),
        ),
        migrations.AddField(
            model_name='article',
            name='gallery_display_mode',
            field=models.CharField(choices=[('carousel', 'Карусель'), ('collage', 'Коллаж')], default='carousel',
                                   max_length=20, verbose_name='Режим отображения галереи'),
        ),
        migrations.AddField(
            model_name='article',
            name='exclude_inline_from_blocks',
            field=models.BooleanField(default=False,
                                      help_text='Если включено, изображения/файлы/ссылки, добавленные через редактор в текст, не будут отображаться в общих блоках',
                                      verbose_name='Не дублировать медиа из редактора в блоках'),
        ),
        migrations.AddField(
            model_name='project',
            name='show_on_homepage',
            field=models.BooleanField(default=False, verbose_name='Показывать на главной'),
        ),
        migrations.AddField(
            model_name='project',
            name='homepage_order',
            field=models.PositiveIntegerField(default=0, verbose_name='Порядок на главной'),
        ),
        migrations.AddField(
            model_name='project',
            name='programming_languages',
            field=models.CharField(blank=True, help_text='Например: Python, JavaScript', max_length=200,
                                   verbose_name='Языки программирования (через запятую)'),
        ),
        migrations.RemoveField(
            model_name='project',
            name='status',
        ),
        migrations.AddField(
            model_name='project',
            name='status',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL,
                                    to='main.projectstatus', verbose_name='Статус'),
        ),
    ]
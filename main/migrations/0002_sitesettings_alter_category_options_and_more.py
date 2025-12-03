from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SiteSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('site_name', models.CharField(default='deev.space', max_length=100, verbose_name='Название сайта')),
                ('site_description', models.TextField(blank=True, verbose_name='Описание сайта')),
                ('owner_name', models.CharField(default='Деев Егор Викторович', max_length=200, verbose_name='Имя владельца')),
                ('owner_title', models.CharField(default='Backend Developer', max_length=200, verbose_name='Должность')),
                ('owner_bio', models.TextField(blank=True, verbose_name='О себе')),
                ('owner_photo', models.ImageField(blank=True, null=True, upload_to='site/', verbose_name='Фото владельца')),
                ('owner_email', models.EmailField(default='egor@deev.space', max_length=254, verbose_name='Email')),
                ('owner_phone', models.CharField(blank=True, max_length=20, verbose_name='Телефон')),
                ('owner_city', models.CharField(default='Москва', max_length=100, verbose_name='Город')),
                ('telegram_url', models.URLField(blank=True, verbose_name='Telegram')),
                ('github_url', models.URLField(blank=True, verbose_name='GitHub')),
                ('vk_url', models.URLField(blank=True, verbose_name='VKontakte')),
                ('linkedin_url', models.URLField(blank=True, verbose_name='LinkedIn')),
                ('resume_file', models.FileField(blank=True, null=True, upload_to='site/', verbose_name='Файл резюме')),
                ('yandex_metrika_id', models.CharField(blank=True, max_length=20, verbose_name='ID Яндекс.Метрики')),
                ('google_analytics_id', models.CharField(blank=True, max_length=20, verbose_name='ID Google Analytics')),
            ],
            options={
                'verbose_name': 'Настройки сайта',
                'verbose_name_plural': 'Настройки сайта',
            },
        ),
        migrations.AlterModelOptions(
            name='category',
            options={'ordering': ['order', 'name'], 'verbose_name': 'Категория', 'verbose_name_plural': 'Категории'},
        ),
        migrations.AlterModelOptions(
            name='customuser',
            options={'ordering': ['-date_joined'], 'verbose_name': 'Пользователь', 'verbose_name_plural': 'Пользователи'},
        ),
        migrations.AlterModelOptions(
            name='skill',
            options={'ordering': ['category', 'order', 'name'], 'verbose_name': 'Навык', 'verbose_name_plural': 'Навыки'},
        ),
        migrations.RemoveField(
            model_name='education',
            name='certificate',
        ),
        migrations.RemoveField(
            model_name='project',
            name='img_icon',
        ),
        migrations.AddField(
            model_name='article',
            name='achievement_date',
            field=models.DateField(blank=True, null=True, verbose_name='Дата достижения'),
        ),
        migrations.AddField(
            model_name='category',
            name='description',
            field=models.TextField(blank=True, verbose_name='Описание'),
        ),
        migrations.AddField(
            model_name='category',
            name='icon',
            field=models.CharField(blank=True, default='fas fa-folder', max_length=50, verbose_name='Иконка'),
        ),
        migrations.AddField(
            model_name='category',
            name='order',
            field=models.PositiveIntegerField(default=0, verbose_name='Порядок'),
        ),
        migrations.AddField(
            model_name='contactmessage',
            name='admin_notes',
            field=models.TextField(blank=True, verbose_name='Заметки администратора'),
        ),
        migrations.AddField(
            model_name='contactmessage',
            name='is_replied',
            field=models.BooleanField(default=False, verbose_name='Отвечено'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='avatar',
            field=models.ImageField(blank=True, null=True, upload_to='avatars/', verbose_name='Аватар'),
        ),
        migrations.AddField(
            model_name='education',
            name='achievements',
            field=models.TextField(blank=True, verbose_name='Достижения (каждое с новой строки)'),
        ),
        migrations.AddField(
            model_name='education',
            name='certificate_number',
            field=models.CharField(blank=True, max_length=100, verbose_name='Номер сертификата'),
        ),
        migrations.AddField(
            model_name='education',
            name='certificate_url',
            field=models.URLField(blank=True, verbose_name='Ссылка на сертификат'),
        ),
        migrations.AddField(
            model_name='education',
            name='education_type',
            field=models.CharField(choices=[('university', 'Высшее образование'), ('course', 'Курс/Сертификат'), ('school', 'Школа/Лицей')], default='university', max_length=20, verbose_name='Тип'),
        ),
        migrations.AddField(
            model_name='education',
            name='icon',
            field=models.CharField(default='fas fa-graduation-cap', max_length=50, verbose_name='Иконка'),
        ),
        migrations.AddField(
            model_name='education',
            name='institution_short',
            field=models.CharField(blank=True, max_length=100, verbose_name='Сокращённое название'),
        ),
        migrations.AddField(
            model_name='experience',
            name='company_url',
            field=models.URLField(blank=True, verbose_name='Сайт компании'),
        ),
        migrations.AddField(
            model_name='experience',
            name='responsibilities',
            field=models.TextField(blank=True, verbose_name='Обязанности (каждая с новой строки)'),
        ),
        migrations.AddField(
            model_name='project',
            name='card_size',
            field=models.CharField(choices=[('featured', 'Главный (большой)'), ('regular', 'Обычный'), ('small', 'Компактный')], default='regular', max_length=20, verbose_name='Размер карточки'),
        ),
        migrations.AddField(
            model_name='project',
            name='features',
            field=models.TextField(blank=True, verbose_name='Особенности (каждая с новой строки)'),
        ),
        migrations.AddField(
            model_name='project',
            name='icon',
            field=models.CharField(default='fas fa-code', max_length=50, verbose_name='Иконка проекта'),
        ),
        migrations.AddField(
            model_name='project',
            name='is_visible',
            field=models.BooleanField(default=True, verbose_name='Отображать'),
        ),
        migrations.AddField(
            model_name='skill',
            name='icon_svg',
            field=models.TextField(blank=True, verbose_name='SVG иконка'),
        ),
        migrations.AlterField(
            model_name='article',
            name='achievement_icon',
            field=models.CharField(blank=True, default='fas fa-trophy', max_length=50, verbose_name='Иконка достижения'),
        ),
        migrations.AlterField(
            model_name='article',
            name='is_achievement',
            field=models.BooleanField(default=False, verbose_name='Это достижение'),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='email',
            field=models.EmailField(blank=True, max_length=254, null=True, verbose_name='Email'),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='is_verified',
            field=models.BooleanField(default=False, verbose_name='Верифицирован'),
        ),
        migrations.AlterField(
            model_name='education',
            name='degree',
            field=models.CharField(max_length=200, verbose_name='Специальность/Программа'),
        ),
        migrations.AlterField(
            model_name='education',
            name='is_current',
            field=models.BooleanField(default=False, verbose_name='В процессе обучения'),
        ),
        migrations.AlterField(
            model_name='experience',
            name='is_current',
            field=models.BooleanField(default=False, verbose_name='Текущее место работы'),
        ),
        migrations.AlterField(
            model_name='project',
            name='demo_url',
            field=models.URLField(blank=True, verbose_name='Демо/Ссылка'),
        ),
        migrations.AlterField(
            model_name='project',
            name='description',
            field=models.TextField(verbose_name='Полное описание'),
        ),
        migrations.AlterField(
            model_name='project',
            name='status',
            field=models.CharField(choices=[('completed', 'Завершён'), ('in_development', 'В разработке'), ('beta', 'Бета')], default='completed', max_length=20, verbose_name='Статус'),
        ),
        migrations.AlterField(
            model_name='skill',
            name='category',
            field=models.CharField(choices=[('backend', 'Backend'), ('frontend', 'Frontend'), ('devops', 'DevOps'), ('database', 'Database'), ('tools', 'Tools')], max_length=20, verbose_name='Категория'),
        ),
        migrations.AlterField(
            model_name='skill',
            name='icon',
            field=models.CharField(blank=True, max_length=100, verbose_name='CSS класс иконки'),
        ),
    ]

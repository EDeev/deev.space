from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('is_verified', models.BooleanField(default=False)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'Пользователь',
                'verbose_name_plural': 'Пользователи',
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, verbose_name='Заголовок')),
                ('slug', models.SlugField(max_length=200, unique=True, verbose_name='URL')),
                ('sub_title', models.CharField(blank=True, max_length=300, verbose_name='Подзаголовок')),
                ('post', models.TextField(verbose_name='Содержание')),
                ('excerpt', models.TextField(blank=True, max_length=500, verbose_name='Краткое описание')),
                ('img', models.ImageField(blank=True, null=True, upload_to='articles/', verbose_name='Изображение')),
                ('author', models.CharField(default='Егор Деев', max_length=100, verbose_name='Автор')),
                ('date', models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Дата обновления')),
                ('views', models.PositiveIntegerField(default=0, verbose_name='Просмотры')),
                ('is_published', models.BooleanField(default=True, verbose_name='Опубликовано')),
                ('is_achievement', models.BooleanField(default=False, verbose_name='Достижение')),
                ('achievement_icon', models.CharField(blank=True, max_length=50, verbose_name='Иконка достижения')),
            ],
            options={
                'verbose_name': 'Статья',
                'verbose_name_plural': 'Статьи',
                'ordering': ['-date'],
            },
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Название')),
                ('slug', models.SlugField(max_length=100, unique=True, verbose_name='URL')),
            ],
            options={
                'verbose_name': 'Категория',
                'verbose_name_plural': 'Категории',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField(max_length=2000, verbose_name='Содержание')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Дата обновления')),
                ('is_approved', models.BooleanField(default=True, verbose_name='Одобрен')),
                ('article', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='main.article', verbose_name='Статья')),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='replies', to='main.comment', verbose_name='Родительский комментарий')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Комментарий',
                'verbose_name_plural': 'Комментарии',
                'ordering': ['created_at'],
            },
        ),
        migrations.CreateModel(
            name='ContactMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Имя')),
                ('email', models.EmailField(max_length=254, verbose_name='Email')),
                ('subject', models.CharField(max_length=200, verbose_name='Тема')),
                ('message', models.TextField(verbose_name='Сообщение')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата')),
                ('is_read', models.BooleanField(default=False, verbose_name='Прочитано')),
            ],
            options={
                'verbose_name': 'Сообщение',
                'verbose_name_plural': 'Сообщения',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Education',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('institution', models.CharField(max_length=300, verbose_name='Учебное заведение')),
                ('degree', models.CharField(max_length=200, verbose_name='Специальность')),
                ('description', models.TextField(blank=True, verbose_name='Описание')),
                ('start_year', models.PositiveIntegerField(verbose_name='Год начала')),
                ('end_year', models.PositiveIntegerField(blank=True, null=True, verbose_name='Год окончания')),
                ('is_current', models.BooleanField(default=False, verbose_name='В процессе')),
                ('certificate', models.CharField(blank=True, max_length=100, verbose_name='Сертификат')),
                ('order', models.PositiveIntegerField(default=0, verbose_name='Порядок')),
            ],
            options={
                'verbose_name': 'Образование',
                'verbose_name_plural': 'Образование',
                'ordering': ['order', '-start_year'],
            },
        ),
        migrations.CreateModel(
            name='Experience',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, verbose_name='Должность')),
                ('company', models.CharField(max_length=200, verbose_name='Компания')),
                ('description', models.TextField(verbose_name='Описание')),
                ('technologies', models.CharField(blank=True, max_length=500, verbose_name='Технологии')),
                ('start_date', models.DateField(verbose_name='Дата начала')),
                ('end_date', models.DateField(blank=True, null=True, verbose_name='Дата окончания')),
                ('is_current', models.BooleanField(default=False, verbose_name='Текущее место')),
                ('order', models.PositiveIntegerField(default=0, verbose_name='Порядок')),
            ],
            options={
                'verbose_name': 'Опыт работы',
                'verbose_name_plural': 'Опыт работы',
                'ordering': ['order', '-start_date'],
            },
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, verbose_name='Название')),
                ('slug', models.SlugField(max_length=200, unique=True, verbose_name='URL')),
                ('description', models.TextField(verbose_name='Описание')),
                ('short_description', models.CharField(max_length=300, verbose_name='Краткое описание')),
                ('img_main', models.ImageField(blank=True, null=True, upload_to='projects/', verbose_name='Главное изображение')),
                ('img_icon', models.CharField(blank=True, max_length=50, verbose_name='Иконка проекта')),
                ('technologies', models.CharField(max_length=500, verbose_name='Технологии (через запятую)')),
                ('github_url', models.URLField(blank=True, verbose_name='GitHub')),
                ('demo_url', models.URLField(blank=True, verbose_name='Демо')),
                ('status', models.CharField(choices=[('completed', 'Завершён'), ('in_development', 'В разработке')], default='completed', max_length=20, verbose_name='Статус')),
                ('users_count', models.CharField(blank=True, max_length=50, verbose_name='Количество пользователей')),
                ('author', models.CharField(default='Егор Деев', max_length=100, verbose_name='Автор')),
                ('date', models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')),
                ('order', models.PositiveIntegerField(default=0, verbose_name='Порядок отображения')),
            ],
            options={
                'verbose_name': 'Проект',
                'verbose_name_plural': 'Проекты',
                'ordering': ['order', '-date'],
            },
        ),
        migrations.CreateModel(
            name='Skill',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Название')),
                ('category', models.CharField(choices=[('frontend', 'Frontend'), ('backend', 'Backend'), ('devops', 'DevOps'), ('database', 'Data Base'), ('tools', 'Tools')], max_length=20, verbose_name='Категория')),
                ('icon', models.CharField(blank=True, max_length=50, verbose_name='Иконка')),
                ('order', models.PositiveIntegerField(default=0, verbose_name='Порядок')),
            ],
            options={
                'verbose_name': 'Навык',
                'verbose_name_plural': 'Навыки',
                'ordering': ['category', 'order'],
            },
        ),
        migrations.AddField(
            model_name='article',
            name='category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='articles', to='main.category', verbose_name='Категория'),
        ),
        migrations.CreateModel(
            name='CommentLike',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_like', models.BooleanField(verbose_name='Лайк')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата')),
                ('comment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comment_likes', to='main.comment', verbose_name='Комментарий')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comment_likes', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Оценка комментария',
                'verbose_name_plural': 'Оценки комментариев',
                'unique_together': {('comment', 'user')},
            },
        ),
        migrations.CreateModel(
            name='ArticleLike',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_like', models.BooleanField(verbose_name='Лайк')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата')),
                ('article', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='likes', to='main.article', verbose_name='Статья')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='article_likes', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Оценка статьи',
                'verbose_name_plural': 'Оценки статей',
                'unique_together': {('article', 'user')},
            },
        ),
    ]

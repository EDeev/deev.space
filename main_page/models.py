from django.db import models


class Articles(models.Model):
    sub_title = models.CharField(max_length=80)
    title = models.CharField(max_length=120)  # тип данных char длинна ограничена в 120 символов
    url = models.TextField(max_length=120)

    post_title = models.CharField(max_length=120)
    post = models.TextField()  # Неограниченное кол-во символов

    img = models.CharField(max_length=80)
    author = models.CharField(max_length=40)
    date = models.DateTimeField()

    def __str__(self):
        return self.title


class Projects(models.Model):
    title = models.CharField(max_length=80)
    url = models.CharField(max_length=120)

    htegs = models.CharField(max_length=40)
    htegs_post = models.CharField(max_length=40)

    img_main = models.CharField(max_length=120)
    img_type = models.CharField(max_length=120)

    author = models.CharField(max_length=40)
    date = models.DateTimeField()

    def __str__(self):
        return self.title


class Skills(models.Model):
    sub_title = models.CharField(max_length=80)
    title = models.CharField(max_length=120)  # тип данных char длинна ограничена в 120 символов
    url = models.TextField(max_length=120)
    tegs = models.CharField(max_length=120)

    post_title = models.CharField(max_length=120)
    post = models.TextField()  # Неограниченное кол-во символов

    img = models.CharField(max_length=80)
    author = models.CharField(max_length=40)
    date = models.DateTimeField()

    def __str__(self):
        return self.title

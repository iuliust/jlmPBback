# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-25 00:43
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('callcenter', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Achievement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('condition', models.CharField(max_length=300)),
            ],
        ),
        migrations.CreateModel(
            name='AchievementUnlock',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('achievement', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='callcenter.Achievement')),
            ],
        ),
        migrations.CreateModel(
            name='NumbersLocation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=6)),
                ('pays', models.CharField(max_length=2)),
                ('zone', models.CharField(max_length=1)),
                ('indicatif', models.CharField(max_length=2)),
                ('location_lat', models.CharField(max_length=20)),
                ('location_long', models.CharField(max_length=20)),
            ],
        ),
        migrations.RemoveField(
            model_name='userextend',
            name='agentKey',
        ),
        migrations.AddField(
            model_name='appel',
            name='date',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='userextend',
            name='address',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='userextend',
            name='location_lat',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='userextend',
            name='location_long',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='userextend',
            name='phi_multiplier',
            field=models.DecimalField(blank=True, decimal_places=1, default=1, max_digits=2, null=True),
        ),
        migrations.AlterField(
            model_name='appel',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='userextend',
            name='agentUsername',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='userextend',
            name='phi',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='userextend',
            name='user',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='UserExtend', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='achievementunlock',
            name='userExtend',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='callcenter.UserExtend'),
        ),
        migrations.AddField(
            model_name='achievement',
            name='unlockers',
            field=models.ManyToManyField(related_name='achievements_aux', through='callcenter.AchievementUnlock', to='callcenter.UserExtend'),
        ),
    ]
# Generated by Django 3.2.12 on 2022-04-05 23:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('degreed', '0019_auto_20220325_1757'),
    ]

    operations = [
        migrations.AlterField(
            model_name='degreedlearnerdatatransmissionaudit',
            name='enterprise_course_enrollment_id',
            field=models.IntegerField(blank=True, db_index=True, null=True),
        ),
        migrations.AlterField(
            model_name='degreedlearnerdatatransmissionaudit',
            name='plugin_configuration_id',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]

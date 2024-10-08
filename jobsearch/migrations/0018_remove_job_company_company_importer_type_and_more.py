# Generated by Django 5.0.6 on 2024-07-02 16:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobsearch', '0017_job_new_company'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='job',
            name='company',
        ),
        migrations.AddField(
            model_name='company',
            name='importer_type',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='company',
            name='importer_name',
            field=models.CharField(help_text='Must match the key from the importer', max_length=255),
        ),
    ]

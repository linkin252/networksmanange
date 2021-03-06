# Generated by Django 3.0.2 on 2020-02-22 16:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('networks', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Day_data',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(verbose_name='数据时间')),
                ('runrate', models.FloatField(default=1.0, verbose_name='运行率')),
                ('ch', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='networks.Channel', verbose_name='日数据')),
            ],
        ),
    ]

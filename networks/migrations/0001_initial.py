# Generated by Django 3.0.2 on 2020-02-22 10:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('instruments', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Network',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Code', models.CharField(max_length=2, verbose_name='台网代码')),
                ('Name', models.CharField(max_length=80, verbose_name='台网名称')),
                ('IDataDir', models.CharField(blank=True, default='', max_length=200, verbose_name='数据目录')),
                ('IOutDir', models.CharField(blank=True, default='', max_length=200, verbose_name='产出目录')),
                ('INetMode', models.IntegerField(choices=[(1, 'Adapt '), (2, 'SeisComp'), (3, 'TDE324')], default=1, verbose_name='台网模式')),
            ],
        ),
        migrations.CreateModel(
            name='Station',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Code', models.CharField(max_length=5, verbose_name='台站代码')),
                ('Name', models.CharField(max_length=80, verbose_name='台站名称')),
                ('fJin', models.FloatField(default=111.11, verbose_name='经度')),
                ('fWei', models.FloatField(default=22.22, verbose_name='经度')),
                ('fHeigth', models.FloatField(default=100, verbose_name='高程')),
                ('fDepth', models.FloatField(default=100, verbose_name='安装深度')),
                ('Network', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='networks.Network', verbose_name='台网名称')),
            ],
        ),
        migrations.CreateModel(
            name='Sta_ADSensor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('SeiralNo', models.IntegerField(default=0, verbose_name='设备顺序号')),
                ('ADSensor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='instruments.AD_Sensor', verbose_name='数采')),
                ('Station', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='networks.Station', verbose_name='台站名称')),
            ],
        ),
        migrations.CreateModel(
            name='Channel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('CHNo', models.IntegerField(default=0, verbose_name='通道顺序号')),
                ('Code_Loc', models.CharField(max_length=2, verbose_name='位置代码')),
                ('Code_CH', models.CharField(max_length=3, verbose_name='通道代码')),
                ('Start_Time', models.DateField(blank=True, verbose_name='开始运转时间')),
                ('End_Time', models.DateField(blank=True, verbose_name='停止运转时间')),
                ('Sta_ADSensor', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='networks.Sta_ADSensor', verbose_name='台站-数采-传感器')),
            ],
        ),
    ]
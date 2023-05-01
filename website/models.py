from django.db import models

# Create your models here.
class Season(models.Model):
    season_id = models.IntegerField(default=1, primary_key=True, null=False)
    season_name = models.CharField(max_length=50, null=True)
    season_prem = models.CharField(max_length=2000, null=True)

    def __str__(self):
        return f"Season {self.season_id}: {self.season_name}"

class Contestants(models.Model):
    id = models.IntegerField(primary_key=True, null=False)
    contestant = models.CharField(max_length=50, null=True)
    age = models.IntegerField(default=20, null=True)
    hometown = models.CharField(max_length=100, null=True)
    season = models.ForeignKey(Season, on_delete=models.CASCADE)

class Results(models.Model):
    number = models.IntegerField(default=1)

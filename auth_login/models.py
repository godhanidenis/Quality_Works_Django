from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    pass

class Reporting_Manager(models.Model):
    Manager_name= models.CharField(max_length=255)

    def __str__(self):
        return self.Manager_name

    class Meta:
        verbose_name='Reporting_Manager'
        verbose_name_plural = 'Reporting_Manager'

class LOB(models.Model):
    User = models.ForeignKey(User, related_name='Teams', on_delete=models.CASCADE)
    Lob_name= models.CharField(max_length=255)

    def __str__(self):
        return self.Lob_name

    class Meta:
        verbose_name='LOB'
        verbose_name_plural = 'LOBs'

class Teams(models.Model):
    Team_name= models.CharField(max_length=255)
    No_agentns= models.IntegerField()
    Locations= models.CharField(max_length=255)
    Reporting_manager= models.ForeignKey(Reporting_Manager, related_name='managers_for_teams', on_delete= models.CASCADE)
    LOB = models.ForeignKey(LOB, related_name='lob_for_teams', on_delete=models.CASCADE)

    def __str__(self):
        return self.Team_name
    
    class Meta:
        verbose_name='Team'
        verbose_name_plural = 'Teams'

class Agents(models.Model):
    Agent_name= models.CharField(max_length=255)
    Agent_id= models.CharField(max_length=255)
    Date_of_join= models.DateField(auto_now_add=True)
    Team=models.ForeignKey(Teams, related_name='Teams_for_agents', on_delete=models.CASCADE)

    def __str__(self):
        return self.Agent_name

    class Meta:
        verbose_name='Agent'
        verbose_name_plural = 'Agents'

class SOP_Types(models.Model):
    User=models.ForeignKey(User, related_name="sop_types_user", on_delete=models.CASCADE)
    Sop_name = models.CharField(max_length=255)

    def __str__(self):
        return self.Sop_name

    class Meta:
        verbose_name='SOP_Types'
        verbose_name_plural = 'SOP_Types'

class SOP(models.Model):
    Sop_types= models.ForeignKey(SOP_Types, related_name='Sop_sub_types', on_delete=models.CASCADE)
    Sop_sub_type=models.CharField(max_length=100)

    def __str__(self):
        return self.Sop_sub_type
    class Meta:
        verbose_name='SOP'
        verbose_name_plural = 'SOPs' 

class Reporting(models.Model):
    User = models.ForeignKey(User, related_name='user_for_reporting', on_delete=models.CASCADE)
    Matrix_type= models.CharField(max_length=255)
    Weights= models.IntegerField()

    class Meta:
        verbose_name='Reporting'
        verbose_name_plural = 'Reporting'
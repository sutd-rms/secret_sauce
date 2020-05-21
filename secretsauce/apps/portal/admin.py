from django.contrib import admin

from .models import *

# Register your models here.

class ProjectAdmin(admin.ModelAdmin):
    fields = ["title", "organization"]

admin.site.register(Project, ProjectAdmin)
admin.site.register(PredictionModel)
admin.site.register(ModelTag)
admin.site.register(Hyperparameters)
admin.site.register(DataBlock)
admin.site.register(Weights)
admin.site.register(ConstraintBlock)
admin.site.register(Constraint)

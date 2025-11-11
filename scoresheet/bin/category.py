from django.db.utils import *
from django.db.models import Q

from scoresheet.models import *

#
# weightcategory
#
weightcategoryList = Weightcategory.objects.all()
for weightcategory in weightcategoryList:
    if not list(weightcategory.minimumweightcategory_set.all()):
        if weightcategory.agecategory.name.startswith('M') or weightcategory.agecategory.name.startswith('W'):
            Minimumweightcategory.objects.create(name='MONDE', weight='0', weightcategory_id=weightcategory.id)
            Minimumweightcategory.objects.create(name='EUROPE', weight='0', weightcategory_id=weightcategory.id)
            Minimumweightcategory.objects.create(name='FRANCE', weight='0', weightcategory_id=weightcategory.id)
            Minimumweightcategory.objects.create(name='REGION', weight='0', weightcategory_id=weightcategory.id)
        else:
            Minimumweightcategory.objects.create(name='DEB', weight='0', weightcategory_id=weightcategory.id)
            Minimumweightcategory.objects.create(name='DPT', weight='0', weightcategory_id=weightcategory.id)
            Minimumweightcategory.objects.create(name='REG', weight='0', weightcategory_id=weightcategory.id)
            Minimumweightcategory.objects.create(name='IRG', weight='0', weightcategory_id=weightcategory.id)
            Minimumweightcategory.objects.create(name='FED', weight='0', weightcategory_id=weightcategory.id)
            Minimumweightcategory.objects.create(name='NAT', weight='0', weightcategory_id=weightcategory.id)
            Minimumweightcategory.objects.create(name='INT B', weight='0', weightcategory_id=weightcategory.id)
            Minimumweightcategory.objects.create(name='INT A', weight='0', weightcategory_id=weightcategory.id)

    # for minimumweightcategory in weightcategory.minimumweightcategory_set.all():
    #     if weightcategory.agecategory.name == 'SENIOR':
    #         senior_minimumweightcategoryList =  Minimumweightcategory.objects.filter(weightcategory_id=weightcategory.id, name=minimumweightcategory.name)
    #         for senior_minimumweightcategory in senior_minimumweightcategoryList:
    #             print("senior = ", senior_minimumweightcategory.name, "weight = ", senior_minimumweightcategory.weight, "senior id = ", senior_minimumweightcategory.id, "mini = ", minimumweightcategory.name, "weight = ", minimumweightcategory.weight)
    #             minimumweightcategory.weight = senior_minimumweightcategory.weight
    #             minimumweightcategory.save()

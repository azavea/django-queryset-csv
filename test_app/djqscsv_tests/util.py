from .models import Person

def create_people_and_get_queryset():
    Person.objects.create(name='vetch', address='iffish', info='wizard')
    Person.objects.create(name='nemmerle', address='roke',
                              info='arch mage')

    return Person.objects.all()


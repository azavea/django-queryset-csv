from .models import Person, Activity

def create_people_and_get_queryset():
    doing_magic = Activity.objects.create(name="Doing Magic")
    resting = Activity.objects.create(name="Resting")

    Person.objects.create(name='vetch', address='iffish',
                          info='wizard', hobby=doing_magic)
    Person.objects.create(name='nemmerle', address='roke',
                          info='deceased arch mage', hobby=resting)
    Person.objects.create(name='ged', address='gont',
                              info='former arch mage', hobby=resting)

    return Person.objects.all()


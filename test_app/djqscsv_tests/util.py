from .models import Person, Activity


def create_people_and_get_queryset():
    doing_magic, _ = Activity.objects.get_or_create(name="Doing Magic")
    resting, _ = Activity.objects.get_or_create(name="Resting")

    Person.objects.get_or_create(name='vetch', address='iffish',
                                 info='wizard', hobby=doing_magic)
    Person.objects.get_or_create(name='nemmerle', address='roke',
                                 info='deceased arch mage', hobby=resting)
    Person.objects.get_or_create(name='ged', address='gont',
                                 info='former arch mage', hobby=resting)

    return Person.objects.all()

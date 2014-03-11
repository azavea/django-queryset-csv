import djqscsv
from models import Person

def get_csv(request):
    qs = Person.objects.all()
    return djqscsv.render_to_csv_response(qs)

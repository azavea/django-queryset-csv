from djqscsv_tests.context import djqscsv
from .util import create_people_and_get_queryset


def get_csv(request):
    qs = create_people_and_get_queryset()
    return djqscsv.render_to_csv_response(qs)

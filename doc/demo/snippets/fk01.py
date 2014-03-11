person_qs = Person.objects.values('id', 'name', 'hobby__name')
render_to_csv_response(person_qs, field_header_map={'hobby__name': 'Name of Activity'})
# column headers will be 'id', 'name', and 'Name of Activity'

from django.db.models import Q


def decorate_get_queryset(f):
    def decorated(self):
        queryset = f(self)
        query_params = self.request.query_params
        url_params = self.kwargs

        # get queryset_filters from FiltersMixin
        queryset_filters = self.get_db_filters(url_params, query_params)

        # This dict will hold filter kwargs to pass in to Django ORM calls.
        db_filters = queryset_filters['db_filters']

        # This dict will hold exclude kwargs to pass in to Django ORM calls.
        db_excludes = queryset_filters['db_excludes']

        query = Q()
        for key, lookup in queryset_filters['db_filters_values'].items():
            lookup_op = lookup[0]
            # If has `IN` already in query to this key, apply it.
            if key+'__in' in db_filters:
                queryset = queryset.filter((key+'__in', db_filters[key+'__in']))
            # Combine all lookups.
            for value in lookup[1]:
                query = query | Q((key + lookup_op, value))

        return queryset.filter(query, **db_filters).exclude(**db_excludes)
    return decorated

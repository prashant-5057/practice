
import operator
from functools import reduce

from django.db import models
from rest_framework import filters
from rest_framework.compat import distinct


class PriorizedSearchFilter(filters.SearchFilter):
    def filter_queryset(self, request, queryset, view):
        """Override to return priorized results."""
        search_fields = getattr(view, 'search_fields', None)
        search_terms = self.get_search_terms(request)

        if not search_fields or not search_terms:
            return queryset

        orm_lookups = [
            self.construct_search(str(search_field))
            for search_field in search_fields
        ]
        base = queryset

        # Will contain a queryset for each search term
        querysets = list()

        for search_term in search_terms:
            queries = [
                models.Q(**{orm_lookup: search_term})
                for orm_lookup in orm_lookups
            ]

            # Conditions for annotated priority value. Priority == inverse of the search field's index.
            # Example:
            #   search_fields = ['field_A', 'field_B', 'field_C']
            #   Priorities are field_A = 2, field_B = 1, field_C = 0
            when_conditions = [models.When(queries[i], then=models.Value(
                len(queries) - i - 1)) for i in reversed(range(len(queries)))]

            # Generate queryset result for this search term, with annotated priority
            querysets.append(
                queryset.filter(reduce(operator.or_, queries))
                .annotate(priority=models.Case(
                    *when_conditions,
                    output_field=models.IntegerField(),
                    default=models.Value(-1))  # Lowest possible priority
                )
            )

        # Intersect all querysets and order by highest priority
        queryset = reduce(operator.and_, querysets).order_by('-priority')

        if self.must_call_distinct(queryset, search_fields):
            queryset = distinct(queryset, base)
        return queryset

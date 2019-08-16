

class BaseQueryService:
    model = None
    select_related = []

    def get_by_id(self, id):
        queryset = self.model.objects \
            .select_related(*self.select_related) \
            .filter(id=id)
        queryset = self.additional_queryset(queryset, {})

        return queryset.first()

    def get_list(self, limit=10, page=1, **params):
        offset = limit * (page - 1)

        queryset = self.model.objects \
            .select_related(*self.select_related)
        queryset = self.additional_queryset(queryset, params)

        return queryset.count(), queryset.all()[offset:offset + limit], offset

    def additional_queryset(self, queryset, params):
        return queryset

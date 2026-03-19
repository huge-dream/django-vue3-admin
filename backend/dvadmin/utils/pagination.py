# -*- coding: utf-8 -*-

"""
@author: 猿小天

@contact: QQ:1638245306

@Created on: 2020/4/16 23:35
"""
from collections import OrderedDict

from django.core import paginator
from django.core.paginator import Paginator as DjangoPaginator, InvalidPage
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "limit"
    max_page_size = 999
    django_paginator_class = DjangoPaginator

    def paginate_queryset(self, queryset, request, view=None):
        """
        Paginate a queryset if required, either returning a
        page object, or `None` if pagination is not configured for this view.
        """
        empty = True

        page_size = self.get_page_size(request)
        if not page_size:
            return None

        paginator = self.django_paginator_class(queryset, page_size)
        page_number = request.query_params.get(self.page_query_param, 1)
        if page_number in self.last_page_strings:
            page_number = paginator.num_pages

        try:
            self.page = paginator.page(page_number)
        except InvalidPage as exc:
            # msg = self.invalid_page_message.format(
            #     page_number=page_number, message=str(exc)
            # )
            # raise NotFound(msg)
            empty = False

        if paginator.num_pages > 1 and self.template is not None:
            # The browsable API should display pagination controls.
            self.display_page_controls = True

        self.request = request

        if not empty:
            self.page = []

        return list(self.page)

    def get_paginated_response(self, data):
        code = 2000
        msg = 'success'
        page = int(self.get_page_number(self.request, paginator)) or 1
        total = self.page.paginator.count if self.page else 0
        limit = int(self.get_page_size(self.request)) or 10
        is_next = self.page.has_next() if self.page else False
        is_previous = self.page.has_previous() if self.page else False

        if not data:
            code = 2000
            msg = "暂无数据"
            data = []

        return Response(OrderedDict([
            ('code', code),
            ('msg', msg),
            ('page', page),
            ('limit', limit),
            ('total', total),
            ('is_next', is_next),
            ('is_previous', is_previous),
            ('data', data)
        ]))

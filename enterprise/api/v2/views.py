# -*- coding: utf-8 -*-
"""
Views for enterprise api version 2 endpoint.
"""
from __future__ import absolute_import, unicode_literals

from logging import getLogger

from edx_rest_framework_extensions.authentication import BearerAuthentication, JwtAuthentication
from rest_framework import filters, permissions, viewsets
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import detail_route, list_route
from rest_framework.exceptions import NotFound
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework_xml.renderers import XMLRenderer
from six.moves.urllib.parse import quote_plus, unquote  # pylint: disable=import-error,ungrouped-imports

from django.conf import settings
from django.http import Http404
from django.utils.decorators import method_decorator

from enterprise import models
from enterprise.api.v1.views import EnterpriseCustomerViewSet
from enterprise.api.filters import EnterpriseCustomerUserFilterBackend, UserFilterBackend
from enterprise.api.pagination import get_paginated_response
from enterprise.api.throttles import ServiceUserThrottle
from enterprise.api.v1 import serializers
from enterprise.api.v1.decorators import enterprise_customer_required, require_at_least_one_query_parameter
from enterprise.api.v1.permissions import HasEnterpriseEnrollmentAPIAccess, IsInEnterpriseGroup
from enterprise.api_client.discovery import CourseCatalogApiClient
from enterprise.constants import COURSE_KEY_URL_PATTERN

LOGGER = getLogger(__name__)


class EnterpriseCustomerViewSetV2(EnterpriseCustomerViewSet):
    """
    API views for the ``enterprise-customer`` API endpoint.
    """

    queryset = models.EnterpriseCustomer.active_customers.all()
    serializer_class = serializers.EnterpriseCustomerSerializer

    USER_ID_FILTER = 'enterprise_customer_users__user_id'
    FIELDS = (
        'uuid', 'slug', 'name', 'catalog', 'active', 'site', 'enable_data_sharing_consent',
        'enforce_data_sharing_consent',
    )
    filter_fields = FIELDS
    ordering_fields = FIELDS

    @detail_route()
    def courses(self, request, pk=None):  # pylint: disable=invalid-name,unused-argument
        """
        Retrieve the list of courses contained within the enterprise catalogs linked to this enterprise.

        Only courses with active course runs are returned. A course run is considered active if it is currently
        open for enrollment, or will open in the future.
        """
        enterprise_customer = self.get_object()
        combined_content_filter = {}
        for catalog in enterprise_customer.enterprise_customer_catalogs.all():
            if catalog.content_filter == {}:
                combined_content_filter = {}
                break
            else:
                pass

        serializer = serializers.EnterpriseCatalogCoursesReadOnlySerializer(courses)

        # Add enterprise related context for the courses.
        serializer.update_enterprise_courses(enterprise_customer, catalog_id=enterprise_customer.catalog)
        return get_paginated_response(serializer.data, request)
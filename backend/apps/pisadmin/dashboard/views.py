from datetime import timedelta

from django.utils import timezone
from django.db.models import Count
from django.db.models.functions import TruncMonth
from rest_framework import serializers, views
from rest_framework.response import Response

from apps.pisadmin.miscprocurement.models import Inquiry
from apps.pissupplier.models import QuotationMaster
from apps.pisadmin.basicinfo.models import Supplier


class BuyerKPISerializer(serializers.Serializer):
    total_inquiries = serializers.IntegerField()
    pending_inquiries = serializers.IntegerField()
    completed_quotes = serializers.IntegerField()
    total_suppliers = serializers.IntegerField()


class BuyerTaskSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    inquiry_no = serializers.CharField()
    status = serializers.CharField()
    created_at = serializers.DateTimeField()


class SupplierKPISerializer(serializers.Serializer):
    total_quotes = serializers.IntegerField()
    pending_quotes = serializers.IntegerField()
    won_quotes = serializers.IntegerField()
    conversion_rate = serializers.FloatField()


class SupplierQuoteSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    inquiry_no = serializers.CharField()
    item_name = serializers.CharField()
    unit = serializers.CharField()
    deadline = serializers.DateTimeField()


class MessageSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    content = serializers.CharField()
    is_read = serializers.BooleanField()
    created_at = serializers.DateTimeField()


class TrendSerializer(serializers.Serializer):
    month = serializers.CharField()
    count = serializers.IntegerField(required=False)
    quotes = serializers.IntegerField(required=False)
    won = serializers.IntegerField(required=False)


class BuyerDashboardSerializer(serializers.Serializer):
    kpi = BuyerKPISerializer()
    tasks = BuyerTaskSerializer(many=True)
    messages = MessageSerializer(many=True)
    trend = TrendSerializer(many=True)


class SupplierDashboardSerializer(serializers.Serializer):
    kpi = SupplierKPISerializer()
    pending_quotes = SupplierQuoteSerializer(many=True)
    messages = MessageSerializer(many=True)
    trend = TrendSerializer(many=True)


class DashboardResponseSerializer(serializers.Serializer):
    buyer = BuyerDashboardSerializer(allow_null=True)
    supplier = SupplierDashboardSerializer(allow_null=True)


class DashboardViewSet(views.APIView):
    """看板数据视图"""

    def get_buyer_kpi(self, user):
        """采购方 KPI 计算"""
        total_inquiries = Inquiry.objects.filter(create_user=user.username).count()
        pending_inquiries = Inquiry.objects.filter(
            create_user=user.username, status__in=[1, 2, 3]
        ).count()
        completed_quotes = QuotationMaster.objects.filter(
            inquiry_no__in=Inquiry.objects.filter(
                create_user=user.username
            ).values('inquiry_no')
        ).count()
        total_suppliers = Supplier.objects.count()
        return {
            'total_inquiries': total_inquiries,
            'pending_inquiries': pending_inquiries,
            'completed_quotes': completed_quotes,
            'total_suppliers': total_suppliers,
        }

    def get_buyer_tasks(self, user):
        """采购方待办任务"""
        inquiries = Inquiry.objects.filter(
            create_user=user.username,
            status__in=[1, 2, 3]
        ).order_by('-create_time')[:10]
        return [
            {
                'id': i.id,
                'title': i.title,
                'inquiry_no': i.inquiry_no,
                'status': dict(Inquiry.STATUS_CHOICES).get(i.status, str(i.status)),
                'created_at': i.create_time,
            }
            for i in inquiries
        ]

    def get_supplier_kpi(self, user):
        """供应商 KPI 计算"""
        total_quotes = QuotationMaster.objects.filter(supplier_code=user.username).count()
        pending_quotes = QuotationMaster.objects.filter(
            supplier_code=user.username, status__in=[1, 2]
        ).count()
        won_quotes = QuotationMaster.objects.filter(
            supplier_code=user.username, is_awarded=1
        ).count()
        conversion_rate = (won_quotes / total_quotes * 100) if total_quotes > 0 else 0.0
        return {
            'total_quotes': total_quotes,
            'pending_quotes': pending_quotes,
            'won_quotes': won_quotes,
            'conversion_rate': round(conversion_rate, 2),
        }

    def get_supplier_pending_quotes(self, user):
        """供应商待报价清单"""
        quotes = QuotationMaster.objects.filter(
            supplier_code=user.username,
            status__in=[1, 2]
        ).order_by('-creattime')[:10]
        result = []
        for q in quotes:
            inquiry = Inquiry.objects.filter(inquiry_no=q.inquiry_no).first()
            result.append({
                'id': q.autoid,
                'inquiry_no': q.inquiry_no,
                'item_name': inquiry.title if inquiry else '',
                'unit': '',
                'deadline': q.quote_deadline,
            })
        return result

    def get_trend_data(self, user, is_buyer=True):
        """近6个月趋势数据"""
        six_months_ago = timezone.now() - timedelta(days=180)
        if is_buyer:
            data = (
                Inquiry.objects.filter(
                    create_user=user.username,
                    create_time__gte=six_months_ago
                )
                .annotate(month=TruncMonth('create_time'))
                .values('month')
                .annotate(count=Count('id'))
                .order_by('month')
            )
            return [
                {'month': d['month'].strftime('%Y-%m'), 'count': d['count']}
                for d in data
            ]
        else:
            data = (
                QuotationMaster.objects.filter(
                    supplier_code=user.username,
                    creattime__gte=six_months_ago
                )
                .annotate(month=TruncMonth('creattime'))
                .values('month')
                .annotate(quotes=Count('id'))
                .order_by('month')
            )
            result = []
            for d in data:
                won = QuotationMaster.objects.filter(
                    supplier_code=user.username,
                    creattime__month=d['month'].month,
                    creattime__year=d['month'].year,
                    is_awarded=1
                ).count()
                result.append({
                    'month': d['month'].strftime('%Y-%m'),
                    'quotes': d['quotes'],
                    'won': won,
                })
            return result

    def get_messages(self, user):
        """消息通知 - 占位实现，后续接入通知系统"""
        return []

    def get_buyer_data(self, user):
        """获取采购方看板数据"""
        return {
            'kpi': self.get_buyer_kpi(user),
            'tasks': self.get_buyer_tasks(user),
            'messages': self.get_messages(user),
            'trend': self.get_trend_data(user, is_buyer=True),
        }

    def get_supplier_data(self, user):
        """获取供应商看板数据"""
        return {
            'kpi': self.get_supplier_kpi(user),
            'pending_quotes': self.get_supplier_pending_quotes(user),
            'messages': self.get_messages(user),
            'trend': self.get_trend_data(user, is_buyer=False),
        }

    def list(self, request):
        """获取看板数据

        Returns role-based dashboard data based on user's permissions.
        - Buyer role: returns buyer dashboard data
        - Supplier role: returns supplier dashboard data
        - Both roles: returns both
        """
        user = request.user
        if not user or not user.is_authenticated:
            return Response({'buyer': None, 'supplier': None})

        # 判断用户角色
        has_supplier_role = QuotationMaster.objects.filter(
            supplier_code=user.username
        ).exists()
        has_buyer_role = Inquiry.objects.filter(
            create_user=user.username
        ).exists()

        buyer_data = None
        supplier_data = None

        if has_buyer_role:
            buyer_data = self.get_buyer_data(user)

        if has_supplier_role:
            supplier_data = self.get_supplier_data(user)

        response_data = {'buyer': buyer_data, 'supplier': supplier_data}

        # 使用序列化器验证响应数据
        serializer = DashboardResponseSerializer(data=response_data)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.validated_data)

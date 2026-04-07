from datetime import timedelta

from django.utils import timezone
from django.db.models import Count, F
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
    quote_timely_rate = serializers.FloatField()


class BuyerTaskSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    inquiry_no = serializers.CharField()
    status = serializers.CharField()
    created_at = serializers.DateTimeField()
    method = serializers.SerializerMethodField()
    quote_deadline = serializers.DateTimeField(allow_null=True, required=False)
    bid_start_time = serializers.DateTimeField(allow_null=True, required=False)
    bid_end_time = serializers.DateTimeField(allow_null=True, required=False)

    def get_method(self, obj):
        if obj.get('buying_method') == 2:
            return '招标'
        return '询价'


class SupplierKPISerializer(serializers.Serializer):
    total_quotes = serializers.IntegerField()
    pending_quotes = serializers.IntegerField()
    won_quotes = serializers.IntegerField()
    conversion_rate = serializers.FloatField()
    quote_timely_rate = serializers.FloatField()
    on_time_quotes = serializers.IntegerField()
    overdue_quotes = serializers.IntegerField()


class SupplierQuoteSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    inquiry_no = serializers.CharField()
    item_name = serializers.CharField()
    unit = serializers.CharField()
    quantity = serializers.CharField(allow_blank=True, required=False)
    status = serializers.IntegerField()
    method = serializers.SerializerMethodField()
    quote_deadline = serializers.DateTimeField(allow_null=True, required=False)
    bid_start_time = serializers.DateTimeField(allow_null=True, required=False)
    bid_end_time = serializers.DateTimeField(allow_null=True, required=False)

    def get_method(self, obj):
        if obj.get('buying_method') == 2:
            return '招标'
        return '询价'


class MessageSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    content = serializers.CharField()
    is_read = serializers.BooleanField()
    created_at = serializers.DateTimeField()


class TrendSerializer(serializers.Serializer):
    month = serializers.CharField(required=False)
    day = serializers.IntegerField(required=False)
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


class DashboardView(views.APIView):
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

        # 供应商报价及时率 = 在截止时间前提交的报价数 / 总报价数
        buyer_quotations = QuotationMaster.objects.filter(
            inquiry_no__in=Inquiry.objects.filter(
                create_user=user.username
            ).values('inquiry_no')
        )
        total_quotes = buyer_quotations.count()
        timely_quotes = buyer_quotations.filter(
            quotetime__isnull=False,
            quote_deadline__isnull=False,
            quotetime__lte=F('quote_deadline')
        ).count()
        quote_timely_rate = round(timely_quotes / total_quotes * 100, 1) if total_quotes > 0 else 0.0

        return {
            'total_inquiries': total_inquiries,
            'pending_inquiries': pending_inquiries,
            'completed_quotes': completed_quotes,
            'total_suppliers': total_suppliers,
            'quote_timely_rate': quote_timely_rate,
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
                'buying_method': i.buying_method,
                'quote_deadline': i.quote_deadline,
                'bid_start_time': i.bid_start_time,
                'bid_end_time': i.bid_end_time,
            }
            for i in inquiries
        ]

    def get_supplier_kpi(self, user):
        """供应商 KPI 计算"""
        # 超级管理员看到所有供应商汇总数据
        if user.is_superuser:
            total_quotes = QuotationMaster.objects.count()
            pending_quotes = QuotationMaster.objects.filter(status__in=[1, 2]).count()
            won_quotes = QuotationMaster.objects.filter(is_awarded=1).count()
        else:
            total_quotes = QuotationMaster.objects.filter(supplier_code=user.username).count()
            pending_quotes = QuotationMaster.objects.filter(
                supplier_code=user.username, status__in=[1, 2]
            ).count()
            won_quotes = QuotationMaster.objects.filter(
                supplier_code=user.username, is_awarded=1
            ).count()
        conversion_rate = (won_quotes / total_quotes * 100) if total_quotes > 0 else 0.0

        # 及时率计算
        if user.is_superuser:
            all_quotes = QuotationMaster.objects.all()
        else:
            all_quotes = QuotationMaster.objects.filter(supplier_code=user.username)
        total_with_deadline = all_quotes.filter(quote_deadline__isnull=False).count()
        on_time_quotes = all_quotes.filter(
            quotetime__isnull=False,
            quote_deadline__isnull=False,
            quotetime__lte=F('quote_deadline')
        ).count()
        overdue_quotes = total_with_deadline - on_time_quotes
        quote_timely_rate = round(on_time_quotes / total_with_deadline * 100, 1) if total_with_deadline > 0 else 0.0

        return {
            'total_quotes': total_quotes,
            'pending_quotes': pending_quotes,
            'won_quotes': won_quotes,
            'conversion_rate': round(conversion_rate, 2),
            'quote_timely_rate': quote_timely_rate,
            'on_time_quotes': on_time_quotes,
            'overdue_quotes': overdue_quotes,
        }

    def get_supplier_pending_quotes(self, user):
        """供应商待报价清单"""
        # 超级管理员看到所有待报价，供应商只看自己的
        if user.is_superuser:
            quotes = QuotationMaster.objects.filter(status__in=[1, 2]).order_by('-creattime')[:10]
        else:
            quotes = QuotationMaster.objects.filter(
                supplier_code=user.username,
                status__in=[1, 2]
            ).order_by('-creattime')[:10]
        result = []
        for q in quotes:
            inquiry = Inquiry.objects.filter(inquiry_no=q.inquiry_no).first()
            # 获取询价单中的数量
            quantity = ''
            unit = ''
            if inquiry:
                from apps.pisadmin.miscprocurement.models import InquiryRfqItem
                item = InquiryRfqItem.objects.filter(inquiry_no=q.inquiry_no).first()
                if item:
                    quantity = item.qty
                    unit = item.unit or ''
            result.append({
                'id': q.autoid,
                'inquiry_no': q.inquiry_no,
                'item_name': inquiry.title if inquiry else '',
                'quantity': quantity,
                'unit': unit,
                'status': q.status,
                'buying_method': q.buying_method,
                'quote_deadline': q.quote_deadline,
                'bid_start_time': q.bid_start_time,
                'bid_end_time': q.bid_end_time,
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
            # 超级管理员看到所有供应商汇总趋势
            if user.is_superuser:
                data = (
                    QuotationMaster.objects.filter(creattime__gte=six_months_ago)
                    .annotate(month=TruncMonth('creattime'))
                    .values('month')
                    .annotate(quotes=Count('autoid'))
                    .order_by('month')
                )
                result = []
                for d in data:
                    won = QuotationMaster.objects.filter(
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
            else:
                data = (
                    QuotationMaster.objects.filter(
                        supplier_code=user.username,
                        creattime__gte=six_months_ago
                    )
                    .annotate(month=TruncMonth('creattime'))
                    .values('month')
                    .annotate(quotes=Count('autoid'))
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

    def get_buyer_trend_daily(self, user):
        """获取采购方当月每日趋势数据"""
        now = timezone.now()
        start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        data = (
            Inquiry.objects.filter(
                create_user=user.username,
                create_time__gte=start_of_month,
                create_time__lte=now
            )
            .extra(select={'day': 'DAY(create_time)'})
            .values('day')
            .annotate(count=Count('id'))
            .order_by('day')
        )
        return [
            {'day': d['day'], 'count': d['count']}
            for d in data
        ]

    def get_supplier_trend_daily(self, user):
        """获取供应商当月每日趋势数据"""
        now = timezone.now()
        start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        if user.is_superuser:
            data = (
                QuotationMaster.objects.filter(
                    creattime__gte=start_of_month,
                    creattime__lte=now
                )
                .extra(select={'day': 'DAY(creattime)'})
                .values('day')
                .annotate(quotes=Count('autoid'))
                .order_by('day')
            )
            result = []
            for d in data:
                won = QuotationMaster.objects.filter(
                    creattime__day=d['day'],
                    creattime__month=now.month,
                    creattime__year=now.year,
                    is_awarded=1
                ).count()
                result.append({
                    'day': d['day'],
                    'quotes': d['quotes'],
                    'won': won,
                })
            return result
        else:
            data = (
                QuotationMaster.objects.filter(
                    supplier_code=user.username,
                    creattime__gte=start_of_month,
                    creattime__lte=now
                )
                .extra(select={'day': 'DAY(creattime)'})
                .values('day')
                .annotate(quotes=Count('autoid'))
                .order_by('day')
            )
            result = []
            for d in data:
                won = QuotationMaster.objects.filter(
                    supplier_code=user.username,
                    creattime__day=d['day'],
                    creattime__month=now.month,
                    creattime__year=now.year,
                    is_awarded=1
                ).count()
                result.append({
                    'day': d['day'],
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
            'trend': self.get_buyer_trend_daily(user),
        }

    def get_supplier_data(self, user):
        """获取供应商看板数据"""
        return {
            'kpi': self.get_supplier_kpi(user),
            'pending_quotes': self.get_supplier_pending_quotes(user),
            'messages': self.get_messages(user),
            'trend': self.get_supplier_trend_daily(user),
        }

    def get(self, request):
        """获取看板数据

        Returns role-based dashboard data based on user's permissions.
        - Buyer role: returns buyer dashboard data
        - Supplier role: returns supplier dashboard data
        - Both roles: returns both
        - Superadmin or no business data: returns empty structure
        """
        user = request.user
        if not user or not user.is_authenticated:
            return Response({'buyer': None, 'supplier': None})

        # 分别判断用户角色，避免一个表不存在影响另一个
        has_supplier_role = False
        has_buyer_role = False

        try:
            has_supplier_role = QuotationMaster.objects.filter(
                supplier_code=user.username
            ).exists()
        except Exception:
            pass

        try:
            has_buyer_role = Inquiry.objects.filter(
                create_user=user.username
            ).exists()
        except Exception:
            pass

        # 超级管理员或有任何角色，始终返回对应看板数据结构
        buyer_data = None
        supplier_data = None

        # 采购方看板：超级管理员或有任何采购记录的用户
        if user.is_superuser or has_buyer_role:
            try:
                buyer_data = self.get_buyer_data(user)
            except Exception:
                buyer_data = {
                    'kpi': {'total_inquiries': 0, 'pending_inquiries': 0, 'completed_quotes': 0, 'total_suppliers': 0, 'quote_timely_rate': 0},
                    'tasks': [],
                    'messages': [],
                    'trend': [],
                }

        # 供应商看板：超级管理员或有任何供应商记录的用户
        if user.is_superuser or has_supplier_role:
            try:
                supplier_data = self.get_supplier_data(user)
            except Exception:
                supplier_data = {
                    'kpi': {'total_quotes': 0, 'pending_quotes': 0, 'won_quotes': 0, 'conversion_rate': 0},
                    'pending_quotes': [],
                    'messages': [],
                    'trend': [],
                }

        response_data = {'buyer': buyer_data, 'supplier': supplier_data}

        # 使用序列化器验证响应数据
        serializer = DashboardResponseSerializer(data=response_data)
        serializer.is_valid(raise_exception=True)

        return Response({'code': 200, 'msg': 'success', 'data': serializer.validated_data})

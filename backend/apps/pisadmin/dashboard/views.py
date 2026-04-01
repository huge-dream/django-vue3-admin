from datetime import timedelta

from django.utils import timezone
from django.db.models import Count
from django.db.models.functions import TruncMonth
from rest_framework.views import APIView
from rest_framework.response import Response

from apps.pisadmin.miscprocurement.models import Inquiry
from apps.pissupplier.models import QuotationMaster
from apps.pisadmin.basicinfo.models import Supplier


def get_buyer_kpi(user):
    """采购方 KPI 计算"""
    total_inquiries = Inquiry.objects.filter(create_user=user.username).count()
    pending_inquiries = Inquiry.objects.filter(create_user=user.username, status__in=[1, 2, 3]).count()
    completed_quotes = QuotationMaster.objects.filter(
        inquiry_no__in=Inquiry.objects.filter(create_user=user.username).values('inquiry_no')
    ).count()
    total_suppliers = Supplier.objects.count()
    return {
        'total_inquiries': total_inquiries,
        'pending_inquiries': pending_inquiries,
        'completed_quotes': completed_quotes,
        'total_suppliers': total_suppliers,
    }


def get_buyer_tasks(user):
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


def get_supplier_kpi(user):
    """供应商 KPI 计算"""
    total_quotes = QuotationMaster.objects.filter(supplier_code=user.username).count()
    pending_quotes = QuotationMaster.objects.filter(supplier_code=user.username, status__in=[1, 2]).count()
    won_quotes = QuotationMaster.objects.filter(supplier_code=user.username, is_awarded=1).count()
    conversion_rate = (won_quotes / total_quotes * 100) if total_quotes > 0 else 0.0
    return {
        'total_quotes': total_quotes,
        'pending_quotes': pending_quotes,
        'won_quotes': won_quotes,
        'conversion_rate': round(conversion_rate, 2),
    }


def get_supplier_pending_quotes(user):
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
            'quantity': 0,
            'unit': '',
            'deadline': q.quote_deadline,
        })
    return result


def get_trend_data(user, is_buyer=True):
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
        # Add won counts
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
    return [{'month': d['month'].strftime('%Y-%m'), 'count': d['count']} for d in data]


def get_messages(user):
    """消息通知 - 占位实现，后续接入通知系统"""
    return []


class DashboardView(APIView):
    """看板数据视图"""

    def get(self, request):
        user = request.user
        if not user or not user.is_authenticated:
            return Response({'buyer': None, 'supplier': None})

        # 判断用户角色
        # 供应商用户：有 supplier_code 在 QuotationMaster 中
        has_supplier_role = QuotationMaster.objects.filter(supplier_code=user.username).exists()
        # 采购方用户：有 create_user 在 Inquiry 中
        has_buyer_role = Inquiry.objects.filter(create_user=user.username).exists()

        response_data = {'buyer': None, 'supplier': None}

        if has_buyer_role:
            response_data['buyer'] = {
                'kpi': get_buyer_kpi(user),
                'tasks': get_buyer_tasks(user),
                'messages': get_messages(user),
                'trend': get_trend_data(user, is_buyer=True),
            }

        if has_supplier_role:
            response_data['supplier'] = {
                'kpi': get_supplier_kpi(user),
                'pending_quotes': get_supplier_pending_quotes(user),
                'messages': get_messages(user),
                'trend': get_trend_data(user, is_buyer=False),
            }

        return Response(response_data)

from rest_framework import serializers


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
    day = serializers.IntegerField(required=False)
    month = serializers.CharField(required=False)
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

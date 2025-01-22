from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum
from django.utils import timezone
from users.models import User
from .models import Commission, Withdrawal, DistributorStats
from .serializers import (
    DistributorSerializer,
    CommissionSerializer,
    WithdrawalSerializer,
    TeamMemberSerializer,
    DistributorStatsSerializer
)
from .services import DistributorService

class DistributorViewSet(viewsets.ModelViewSet):
    """分销商视图集"""
    serializer_class = DistributorSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.action == 'list':
            # 只有管理员可以查看所有分销商
            if self.request.user.is_staff:
                return User.objects.filter(role__gt=1)
        return User.objects.filter(id=self.request.user.id)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """获取分销统计数据"""
        stats = DistributorService.update_stats(request.user)
        serializer = DistributorStatsSerializer(stats)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def team(self, request):
        """获取团队成员列表"""
        team_members = User.objects.filter(parent=request.user)
        serializer = TeamMemberSerializer(team_members, many=True)
        return Response(serializer.data)

class CommissionViewSet(viewsets.ReadOnlyModelViewSet):
    """佣金记录视图集"""
    serializer_class = CommissionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Commission.objects.filter(distributor=self.request.user)

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """获取佣金汇总数据"""
        total = self.get_queryset().aggregate(
            total_amount=Sum('amount'),
            settled_amount=Sum('amount', filter=models.Q(status='settled')),
            pending_amount=Sum('amount', filter=models.Q(status='pending'))
        )
        return Response({
            'total_amount': total['total_amount'] or 0,
            'settled_amount': total['settled_amount'] or 0,
            'pending_amount': total['pending_amount'] or 0
        })

class WithdrawalViewSet(viewsets.ModelViewSet):
    """提现申请视图集"""
    serializer_class = WithdrawalSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Withdrawal.objects.filter(distributor=self.request.user)

    def perform_create(self, serializer):
        withdrawal = serializer.save(distributor=self.request.user)
        # 冻结提现金额
        self.request.user.balance -= withdrawal.amount
        self.request.user.save()

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """取消提现申请"""
        withdrawal = self.get_object()
        if withdrawal.status != 'pending':
            return Response(
                {'detail': '只能取消待审核的提现申请'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 返还提现金额
        withdrawal.distributor.balance += withdrawal.amount
        withdrawal.distributor.save()
        
        withdrawal.status = 'cancelled'
        withdrawal.handled_at = timezone.now()
        withdrawal.save()
        
        return Response({'detail': '提现申请已取消'})
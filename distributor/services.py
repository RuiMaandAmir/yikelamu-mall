from django.db.models import Sum, Count, Max, Q
from django.utils import timezone
from django.db import transaction
from datetime import datetime, time, timedelta
from users.models import User
from trade.models import Order
from .models import (
    DistributorStats,
    DistributorReport,
    Commission,
    Withdrawal,
    WithdrawalAudit,
    UpgradeRule,
    UpgradeRecord
)

class DistributorService:
    @staticmethod
    def update_stats(user):
        """更新分销商统计数据"""
        stats, _ = DistributorStats.objects.get_or_create(distributor=user)
        
        # 计算总销售额和订单数
        orders = user.distributed_orders.all()
        total_sales = orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        order_count = orders.count()
        last_order = orders.order_by('-created_at').first()
        
        # 计算总佣金
        total_commission = user.commissions.filter(
            status='settled'
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        # 计算团队人数
        team_size = User.objects.filter(parent=user).count()
        
        # 更新统计数据
        stats.total_sales = total_sales
        stats.total_commission = total_commission
        stats.team_size = team_size
        stats.order_count = order_count
        if last_order:
            stats.last_order_time = last_order.created_at
        stats.save()

        return stats

class ReportService:
    @staticmethod
    def generate_daily_report(date=None):
        """生成日报"""
        if date is None:
            date = timezone.now().date()

        # 获取当日数据
        start_time = timezone.make_aware(datetime.combine(date, time.min))
        end_time = timezone.make_aware(datetime.combine(date, time.max))

        # 统计订单数据
        orders = Order.objects.filter(created_at__range=(start_time, end_time))
        total_sales = orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0

        # 统计佣金数据
        commissions = Commission.objects.filter(created_at__range=(start_time, end_time))
        total_commission = commissions.aggregate(Sum('amount'))['amount__sum'] or 0

        # 统计分销商数据
        distributors = User.objects.filter(role__gt=1)
        new_distributors = distributors.filter(date_joined__range=(start_time, end_time))
        active_distributors = distributors.filter(
            distributed_orders__created_at__range=(start_time, end_time)
        ).distinct()

        # 统计提现数据
        withdrawals = Withdrawal.objects.filter(
            created_at__range=(start_time, end_time),
            status='completed'
        )
        withdrawal_amount = withdrawals.aggregate(Sum('amount'))['amount__sum'] or 0

        # 创建或更新报表
        report, _ = DistributorReport.objects.update_or_create(
            period='daily',
            date=date,
            defaults={
                'total_sales': total_sales,
                'total_commission': total_commission,
                'order_count': orders.count(),
                'distributor_count': distributors.count(),
                'new_distributor_count': new_distributors.count(),
                'active_distributor_count': active_distributors.count(),
                'withdrawal_amount': withdrawal_amount,
            }
        )
        return report

    @staticmethod
    def generate_weekly_report(date=None):
        """生成周报"""
        if date is None:
            date = timezone.now().date()

        # 获取本周的开始和结束日期
        week_start = date - timedelta(days=date.weekday())
        week_end = week_start + timedelta(days=6)

        # 汇总每日报表数据
        daily_reports = DistributorReport.objects.filter(
            period='daily',
            date__range=(week_start, week_end)
        )

        report, _ = DistributorReport.objects.update_or_create(
            period='weekly',
            date=week_start,
            defaults={
                'total_sales': daily_reports.aggregate(Sum('total_sales'))['total_sales__sum'] or 0,
                'total_commission': daily_reports.aggregate(Sum('total_commission'))['total_commission__sum'] or 0,
                'order_count': daily_reports.aggregate(Sum('order_count'))['order_count__sum'] or 0,
                'distributor_count': daily_reports.last().distributor_count if daily_reports.exists() else 0,
                'new_distributor_count': daily_reports.aggregate(Sum('new_distributor_count'))['new_distributor_count__sum'] or 0,
                'active_distributor_count': daily_reports.aggregate(Max('active_distributor_count'))['active_distributor_count__max'] or 0,
                'withdrawal_amount': daily_reports.aggregate(Sum('withdrawal_amount'))['withdrawal_amount__sum'] or 0,
            }
        )
        return report

    @staticmethod
    def generate_monthly_report(date=None):
        """生成月报"""
        if date is None:
            date = timezone.now().date()

        # 获取本月的开始和结束日期
        month_start = date.replace(day=1)
        next_month = month_start + timedelta(days=32)
        month_end = next_month.replace(day=1) - timedelta(days=1)

        # 汇总每日报表数据
        daily_reports = DistributorReport.objects.filter(
            period='daily',
            date__range=(month_start, month_end)
        )

        report, _ = DistributorReport.objects.update_or_create(
            period='monthly',
            date=month_start,
            defaults={
                'total_sales': daily_reports.aggregate(Sum('total_sales'))['total_sales__sum'] or 0,
                'total_commission': daily_reports.aggregate(Sum('total_commission'))['total_commission__sum'] or 0,
                'order_count': daily_reports.aggregate(Sum('order_count'))['order_count__sum'] or 0,
                'distributor_count': daily_reports.last().distributor_count if daily_reports.exists() else 0,
                'new_distributor_count': daily_reports.aggregate(Sum('new_distributor_count'))['new_distributor_count__sum'] or 0,
                'active_distributor_count': daily_reports.aggregate(Max('active_distributor_count'))['active_distributor_count__max'] or 0,
                'withdrawal_amount': daily_reports.aggregate(Sum('withdrawal_amount'))['withdrawal_amount__sum'] or 0,
            }
        )
        return report

class WithdrawalService:
    @staticmethod
    def process_withdrawal(withdrawal, action, auditor, remark=''):
        """处理提现申请"""
        with transaction.atomic():
            if action == 'approve':
                if withdrawal.status != 'pending':
                    raise ValueError('只能审核待处理的提现申请')
                withdrawal.status = 'approved'
                
            elif action == 'reject':
                if withdrawal.status != 'pending':
                    raise ValueError('只能审核待处理的提现申请')
                withdrawal.status = 'rejected'
                # 返还提现金额
                withdrawal.distributor.balance += withdrawal.amount
                withdrawal.distributor.save()
                
            elif action == 'complete':
                if withdrawal.status != 'approved':
                    raise ValueError('只能完成已审核通过的提现申请')
                withdrawal.status = 'completed'
                
            else:
                raise ValueError('无效的操作')
            
            withdrawal.handled_by = auditor
            withdrawal.handled_at = timezone.now()
            withdrawal.save()
            
            # 创建审核记录
            WithdrawalAudit.objects.create(
                withdrawal=withdrawal,
                auditor=auditor,
                action=action,
                remark=remark
            )
            
            return withdrawal

class UpgradeService:
    @staticmethod
    def check_upgrade(user):
        """检查分销商是否满足升级条件"""
        if not hasattr(user, 'stats'):
            return False

        stats = user.stats
        current_level = user.role
        
        # 获取下一级别的升级规则
        next_rule = UpgradeRule.objects.filter(
            target_level=current_level + 1,
            is_active=True
        ).first()

        if not next_rule:
            return False

        # 计算注册天数
        duration_days = (timezone.now() - user.date_joined).days
        
        # 计算直推人数
        direct_members = User.objects.filter(parent=user).count()

        # 检查是否满足升级条件
        if (stats.total_sales >= next_rule.min_sales and 
            stats.team_size >= next_rule.min_team_size and
            direct_members >= next_rule.min_direct_members and
            duration_days >= next_rule.min_duration_days):
            
            # 创建升级记录
            UpgradeRecord.objects.create(
                distributor=user,
                from_level=current_level,
                to_level=next_rule.target_level,
                total_sales=stats.total_sales,
                team_size=stats.team_size,
                direct_members=direct_members,
                duration_days=duration_days
            )
            
            # 更新用户等级
            user.role = next_rule.target_level
            user.save()
            
            return True

        return False

    @staticmethod
    def check_all_upgrades():
        """检查所有分销商的升级条件"""
        distributors = User.objects.filter(role__gt=0, role__lt=3)
        for distributor in distributors:
            UpgradeService.check_upgrade(distributor)
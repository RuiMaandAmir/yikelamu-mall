from celery import shared_task
from django.utils import timezone
from django.db import transaction
from .services import (
    DistributorService,
    ReportService,
    UpgradeService
)

@shared_task
def update_all_distributor_stats():
    """更新所有分销商的统计数据"""
    from users.models import User
    distributors = User.objects.filter(role__gt=1)  # 获取所有分销商
    for distributor in distributors:
        update_distributor_stats.delay(distributor.id)

@shared_task
def update_distributor_stats(user_id):
    """更新单个分销商的统计数据"""
    try:
        from users.models import User
        with transaction.atomic():
            user = User.objects.get(id=user_id)
            DistributorService.update_stats(user)
    except User.DoesNotExist:
        pass

@shared_task
def generate_daily_report():
    """生成每日报表"""
    date = timezone.now().date()
    ReportService.generate_daily_report(date)

@shared_task
def generate_weekly_report():
    """生成每周报表"""
    date = timezone.now().date()
    ReportService.generate_weekly_report(date)

@shared_task
def generate_monthly_report():
    """生成每月报表"""
    date = timezone.now().date()
    ReportService.generate_monthly_report(date)

@shared_task
def check_distributor_upgrades():
    """检查所有分销商是否满足升级条件"""
    UpgradeService.check_all_upgrades()

@shared_task
def process_commission_settlement():
    """处理佣金结算"""
    from .models import Commission
    # 获取所有待结算的佣金记录
    pending_commissions = Commission.objects.filter(
        status='pending',
        order__status='completed',  # 只处理已完成订单的佣金
        order__completed_at__lte=timezone.now() - timezone.timedelta(days=7)  # 7天后自动结算
    )

    for commission in pending_commissions:
        try:
            with transaction.atomic():
                # 更新佣金状态
                commission.status = 'settled'
                commission.settled_at = timezone.now()
                commission.save()

                # 更新分销商余额
                distributor = commission.distributor
                distributor.balance += commission.amount
                distributor.save()

                # 更新分销商统计数据
                DistributorService.update_stats(distributor)
        except Exception as e:
            # 记录错误日志
            print(f"Error processing commission {commission.id}: {str(e)}")

@shared_task
def clean_expired_withdrawals():
    """清理过期的提现申请"""
    from .models import Withdrawal
    # 获取所有超过30天未处理的待审核提现申请
    expired_withdrawals = Withdrawal.objects.filter(
        status='pending',
        created_at__lte=timezone.now() - timezone.timedelta(days=30)
    )

    for withdrawal in expired_withdrawals:
        try:
            with transaction.atomic():
                # 更新提现状态为已取消
                withdrawal.status = 'cancelled'
                withdrawal.handled_at = timezone.now()
                withdrawal.save()

                # 返还提现金额
                distributor = withdrawal.distributor
                distributor.balance += withdrawal.amount
                distributor.save()

                # 创建审核记录
                withdrawal.audits.create(
                    action='reject',
                    remark='系统自动取消：申请超过30天未处理'
                )
        except Exception as e:
            # 记录错误日志
            print(f"Error cleaning withdrawal {withdrawal.id}: {str(e)}")

@shared_task
def sync_team_stats():
    """同步团队统计数据"""
    from users.models import User
    distributors = User.objects.filter(role__gt=1)

    for distributor in distributors:
        try:
            # 更新团队销售额和人数
            team_members = User.objects.filter(
                models.Q(parent=distributor) |
                models.Q(parent__parent=distributor) |
                models.Q(parent__parent__parent=distributor)
            )
            
            team_sales = sum(
                member.stats.total_sales 
                for member in team_members 
                if hasattr(member, 'stats')
            )
            
            stats = distributor.stats
            stats.team_size = team_members.count()
            stats.team_sales = team_sales
            stats.save()
        except Exception as e:
            # 记录错误日志
            print(f"Error syncing team stats for distributor {distributor.id}: {str(e)}")

@shared_task
def notify_upgrade_qualification():
    """通知符合升级条件的分销商"""
    from users.models import User
    from .models import UpgradeRule
    
    distributors = User.objects.filter(role__gt=0, role__lt=3)
    
    for distributor in distributors:
        try:
            stats = distributor.stats
            next_rule = UpgradeRule.objects.filter(
                target_level=distributor.role + 1,
                is_active=True
            ).first()
            
            if next_rule:
                # 检查是否接近达到升级条件
                sales_progress = stats.total_sales / next_rule.min_sales * 100
                team_progress = stats.team_size / next_rule.min_team_size * 100
                
                if sales_progress >= 80 or team_progress >= 80:
                    # TODO: 发送通知
                    print(f"Distributor {distributor.username} is close to upgrade!")
        except Exception as e:
            # 记录错误日志
            print(f"Error checking upgrade qualification for distributor {distributor.id}: {str(e)}")
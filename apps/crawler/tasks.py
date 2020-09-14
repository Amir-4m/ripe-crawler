from celery.schedules import crontab
from celery.task import periodic_task
from .crawler import RipeCrawler
from .models import RangeIP


@periodic_task(run_every=(crontab(hour='0', minute='0', second='0')), name="check_ip_ranges", ignore_result=True)
def check_ip_ranges():
    qs = RangeIP.objects.all()
    crawled_ips = RipeCrawler().get_organization_ip_range()
    db_existed_ips = qs.values_list('inet', flat=True)
    for ip in crawled_ips.difference(set(db_existed_ips)):
        RangeIP.objects.create(inet=ip)
    for ip in set(db_existed_ips).difference(crawled_ips):
        qs.filter(inet=ip).delete()

import datetime
# 获取当天日期
from logger import C_logger
import logging
import db


def get_now():
    return datetime.datetime.now()


def get_today():
    return datetime.date.today()


# 获取前天日期
def get_previous_date():
    yesterday = datetime.date.today() + datetime.timedelta(days=-1)  # 昨天日期
    return yesterday


# 获取前一个月日期
def get_pervious_month_date():
    r_date = datetime.date.today() + datetime.timedelta(days=-30)
    return r_date


# 获取前一季度日期
def get_pervious_quarter_date():
    r_date = datetime.date.today() + datetime.timedelta(days=-90)
    return r_date


# 获取前一年日期
def get_pervious_year_date():
    r_date = datetime.date.today() + datetime.timedelta(days=-360)
    return r_date


# 获取比今天早多少d的日期
def get_assign_year_date(d):
    r_date = datetime.date.today() + datetime.timedelta(days=-d)
    return r_date


# 转化结果为pyecharts容易接受的格式 字典+列表格式
def change_2_pyechart_format(raw_data):
    format_data = {}
    ser_id = []
    ser_name = []  # 商户名称
    amo = []
    sat = []  # 满意
    cri = []  # 批评
    pri = []  # 表扬
    for res in raw_data:
        ser_id.append(res[0])
        ser_name.append(res[1])
        amo.append(res[2])
        sat.append(res[3])
        pri.append(res[4])
        cri.append(res[5])
    format_data['id'] = ser_id
    format_data['name'] = ser_name
    format_data['amo'] = amo
    format_data['sat'] = sat
    format_data['cri'] = cri
    format_data['pri'] = pri
    return format_data


# 转化结果为increase表
def change_2_pyechart_incresa_format(raw_data):
    format_data = {}
    ser_id = []
    ser_name = []  # 商户名称
    amo = []
    for res in raw_data:
        ser_id.append(res[0])
        ser_name.append(res[1])
        amo.append(res[2])
    format_data['id'] = ser_id
    format_data['name'] = ser_name
    format_data['amo'] = amo
    return format_data


# 获取 时间段 某个类目下商户情况
def get_item_merchants_timelaspes_increase(session, item_id, day_near, day_far):
    previous_day_info = db.query_date_feedback_info(session, item_id, day_far)
    today_info = db.query_date_feedback_info(session, item_id, day_near)
    # 前提一定要保证现在数据库商户和年前的都相同  -> check_merchants

    ret_list = []
    # 以当前商户数据为标准进行对比  O(n²)待优化
    for i in range(len(today_info)):
        for k in range(len(previous_day_info)):
            if today_info[i].merchantId == previous_day_info[k].merchantId:
                single_info = (today_info[i].merchantId, today_info[i].merchantName,
                               today_info[i].amount - previous_day_info[k].amount)
                ret_list.append(single_info)
                break
        # 没匹配到 八说 直接给鸭蛋
        if k == len(previous_day_info) - 1:
            single_info = (today_info[i].merchantId, today_info[i].merchantName, 0)
            ret_list.append(single_info)

    today_format_info = change_2_pyechart_incresa_format(ret_list)  # 转化格式

    # 字典 pyecharts易接受
    incre_res = {'id': today_format_info.get('id'),
                 'name': today_format_info.get('name'),
                 'increment': today_format_info.get('amo')}
    return incre_res


# 取得单例模式的日志ogger对象
def get_single_logger():
    # 第一个c_level,第二个f_level 控制日志等级
    log = C_logger('./log/sys.log', logging.DEBUG, logging.INFO).get_logger()
    return log

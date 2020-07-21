# -*- coding = utf-8 -*-
# @Time :2020/7/5 10:48 下午
# @Author: XZL
# @File : check_update.py
# @Software: PyCharm

import spider
# 这是每次定时任务的执行流程
import tools
import db

log = tools.get_single_logger()  # 日志模块


def main():
    db_path = 'sqlite:///96345.db?check_same_thread=False'
    param = {"code": "server_content"}
    base_url = "http://www.sx96345.com"
    header = "/centre/life_service/"  # url后面跟着的一点

    session = db.get_db_session(db_path, True)
    # 查询所有服务类目
    # every_day_update_feedback(param, base_url, header, session, 0)
    every_day_update_feedback(param, base_url, header, session, 1)
    # all_merchant_info = spider.get_all_pages_service_info(base_url, header, param, '5')
    # all_merchant_info_detail = spider.get_personal_service_data(all_merchant_info)
    # check_merchants(session, 5, all_merchant_info)


# 每日天需要进行第一次爬取数据并进行数据的插入操作
def every_day_update_feedback(param, base_url, header, session, flag):
    item = db.query_all_item(session)

    for i in item:
        item_id = i.id
        item_merchant_amount = i.serviceAmount
        all_merchant_info = spider.get_all_pages_service_info(base_url, header, param, str(item_id))
        all_merchant_info_detail = spider.get_personal_service_data(all_merchant_info)

        if flag == 0:
            # 每天插入第一次数据时进行商户完整性检查  是否有更新/删除
            check_merchants(session, item_id, all_merchant_info, item_merchant_amount)
            # 当天第一次更新反馈信息 插入新row
            db.insert_feedback(session, all_merchant_info_detail)
        elif flag == 1:
            db.update_feedback(session, all_merchant_info_detail, tools.get_today())
        # 插入最近更新时间
        db.update_updateTime(session, item_id)


# 判断一个服务类目中的商家是否发生改变 并修改数据库信息
# 商户总数增加 -> 找出新加入 -> 数据库就加信息 / 商户总数减少 ->找出删除的商户 -> 删除删去商户所有信息


def every_day_update_feedback2(param, base_url, header, session, flag):
    all_merchant_info = spider.get_all_pages_service_info(base_url, header, param, '1')
    all_merchant_info_detail = spider.get_personal_service_data(all_merchant_info)

    if flag == 0:
        db.insert_feedback(session, all_merchant_info_detail)
    elif flag == 1:
        db.update_feedback(session, all_merchant_info_detail, tools.get_today())


# 这个操作建议每天早上insert是进行check
def check_merchants(session, item_id, current_all_info, item_merchant_amount):
    previous_merchants = db.query_merchant_info(session, item_id)  # 返回的是元祖，得拆分
    previous_merchants_id = []  # 数据库中存储的id
    current_merchant_id = []  # 当前所有商户id

    # 填充两个list
    for i in previous_merchants:
        previous_merchants_id.append(i.merchantId)
    for i in current_all_info:
        current_merchant_id.append(i.get('id'))

    # 用差集的特性来效验增加或减少的商户 机智如我
    differ_p_n = set(previous_merchants_id).difference(set(current_merchant_id))  # p-n
    differ_n_p = set(current_merchant_id).difference(set(previous_merchants_id))  # n-p

    decrease = list(differ_p_n)  # set转list才能取值操作
    increase = list(differ_n_p)

    decrease_mount = len(decrease)  # 下降的人数
    increase_mount = len(increase)  # 增加的人数

    if increase_mount > 0:  # 查找新增商户，并插入数据库中
        for t in range(increase_mount):
            for i in range(len(current_all_info)):
                if increase[t] == current_all_info[i].get('id'):
                    db.insert_merchant(session, current_all_info[i])
                    log.warning("新增商家->", current_all_info[i])
                    break

    if decrease_mount > 0:
        for k in range(decrease_mount):
            for i in previous_merchants:
                if i.merchantId == decrease[k]:
                    log.warning("删除商家->", i)
                    # 删除商家
                    db.del_merchant(session, i)
                    # 删除该商家对于的所有反馈信息
                    db.delete_merchant_feedback(session, i)
                    break

    # 更新item表
    if decrease_mount > 0 or increase_mount > 0 or len(current_all_info) != item_merchant_amount:
        db.update_item(session, item_id, len(current_all_info))


if __name__ == '__main__':
    main()

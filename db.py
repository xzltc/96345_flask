from sqlalchemy import create_engine, exc
from sqlalchemy.orm import sessionmaker
from entity import Item, Feedback, Merchant
import tools

log = tools.get_single_logger()  # 日志模块


# 获取数据库session实例
def get_db_session(path, echo_mode=False):
    # 创建Session 数据库相关操作
    log.debug("------------------数据库连接开始------------------\n")
    try:
        engine = create_engine(path, echo=echo_mode)
        Session = sessionmaker(bind=engine)
        session = Session()
        log.debug("-------------------数据库已连接------------------\n")
        return session
    except exc.SQLAlchemyError as e:
        log.error(" !!!!!连接出错!!!!! ------>  %s" % e)


# 查询给定类目
def query_assign_item(session, item_id):
    try:
        our_item = session.query(Item).filter_by(id=item_id).first()
        return our_item
    except exc.SQLAlchemyError as e:
        log.error("查询类目%d出错 %s" % (item_id, e))


# 查询所有类目
def query_all_item(session):
    try:
        our_item = session.query(Item).all()
        log.info("查询所有类目成功！")
        return our_item
    except exc.SQLAlchemyError as e:
        log.error("查询所有类目出错！")


# 更新指定类目下商家总数
def update_item(session, item_id, service_amount):
    try:
        session.query(Item).filter_by(id=item_id).update({"serviceAmount": service_amount})
        session.commit()
        log.info("更新类目:%s -> 总数为 %d 成功!!" % (item_id, service_amount))
    except exc.SQLAlchemyError as e:
        log.error("更新类目:%s -> 总数为 %d 失败" % (item_id, service_amount))


def update_feedback(session, all_info, date):
    for i in all_info:
        session.query(Feedback).filter(Feedback.merchantId == i.get('id')).filter(
            Feedback.createTime == date).update(
            {'satisfaction': i.get('satisfaction'), 'praise': i.get('praise'),
             'criticism': i.get('criticism'), 'amount': i.get('amount')})
    try:
        session.commit()
        log.info("更新%s反馈信息成功！" % str(date))
    except exc.SQLAlchemyError as e:
        log.error("更新%s反馈信息失败！" % str(date))


# 批量插入用户反馈信息
def insert_feedback(session, all_info):
    log.debug("------------------更新反馈启动------------------\n")
    try:
        feedback_list = []
        for i in all_info:
            feedback = Feedback(merchantId=i['id'], itemId=i['item'], satisfaction=i['satisfaction'],
                                praise=i['praise'],
                                criticism=i['criticism'], amount=i['amount'])
            print(feedback.__repr__())
            feedback_list.append(feedback)
        session.add_all(feedback_list)
        session.commit()
        log.info("每日首次插入feedback数据成功！！")
        log.debug("------------------更新反馈结束------------------\n")
    except exc.SQLAlchemyError as e:
        log.error("每日首次插入feedback数据失败！！")


# 批量插入商户信息
def insert_merchant(session, info):
    log.debug("------------------更新商户启动------------------\n")
    # 遍历拼接merchant信息，append进提交lists中
    merchant = Merchant(merchantId=info['id'], itemId=info['item'], merchantName=info['name'], href=info['href'])
    try:
        session.add(merchant)
        session.commit()
        log.info("插入一个商户信息成功！！Id:%d Item:%d Name:%s"%(info['id'],info['item'],info['name']))
        log.debug("------------------更新商户结束------------------\n")
    except exc.SQLAlchemyError as e:
        log.error("插入一个商户信息失败！！")


# 查询指定类目的商户信息
def query_merchart_detail_info(session, item_id):
    log.debug("------------------查询商户详细信息开始------------------\n")
    # 由item_id -> merchant查询到商户 -> 取得merchanId -> feedback表信息
    try:
        results = session.query(Merchant.merchantId, Merchant.merchantName, Feedback.amount, Feedback.satisfaction,
                                Feedback.praise, Feedback.criticism, Feedback.createTime).join(Feedback,
                                                                                               Merchant.merchantId == Feedback.merchantId) \
            .filter(Merchant.itemId == item_id).filter(Feedback.itemId == item_id) \
            .order_by(Feedback.amount.desc()).all()

        log.debug("查询结果数：", len(results))
        for r in results:
            log.debug(r)
        log.info("查询商户详细信息成功 总数为%d" % len(results))
        log.debug("------------------查询商户详细信息结束------------------\n")
        return results
    except exc.SQLAlchemyError as e:
        log.error("查询商户详细信息失败！！")


def query_merchant_info(session, item_id):
    log.debug("------------------查询商户信息开始------------------\n")
    # 获得当前类目下的所有商户
    try:
        results = session.query(Merchant).filter(Merchant.itemId == item_id).all()
        print("查询结果数：", len(results))
        for r in results:
            log.debug(r)
        log.info("查询merchant成功！！")
        log.debug("------------------查询商户信息结束------------------\n")
        return results
    except exc.SQLAlchemyError as e:
        log.error("查询merchant失败！！")


# 查询当前该类目下所有商户某天服务反馈信息
def query_date_feedback_info(session, item_id, assign_date):
    item = query_assign_item(session, item_id)
    log.debug("------------开始查询日期： %s %s 的服务情况---------------\n" % (assign_date, item.serviceName))
    try:
        results = session.query(Merchant.merchantId, Merchant.merchantName, Feedback.amount, Feedback.satisfaction,
                                Feedback.praise, Feedback.criticism).join(Feedback,
                                                                          Merchant.merchantId == Feedback.merchantId).filter(
            Merchant.itemId == item_id).filter(Feedback.itemId == item_id).filter(
            Feedback.createTime == assign_date).order_by(Feedback.amount.desc()).all()
        log.debug("查询结果数：%d " % len(results))
        for r in results:
            log.debug(r)
        log.debug("-------------------查询当前日期结束------------------\n")
        return results
    except exc.SQLAlchemyError as e:
        log.error("查询merchant失败！！")


# 删除一个商户
def del_merchant(session, merchant_info):
    try:
        session.query(Merchant).filter(Merchant.merchantId == merchant_info.merchantId).filter(
            Merchant.itemId == merchant_info.itemId).delete()
        session.commit()
        log.warning("删除一个商户成功 ID:%d" % merchant_info.merchantId)
    except exc.SQLAlchemyError as e:
        log.error("删除一个商户失败！！ID:%d" % merchant_info.merchantId)


# 删除这个商户相关的所有feedback信息
def delete_merchant_feedback(session, merchant_info):
    try:
        session.query(Feedback).filter(Feedback.merchantId == merchant_info.merchantId).filter(
            Feedback.itemId == merchant_info.itemId).delete()
        session.commit()
        log.warning("删除商户相关的所有feedback信息 ID:%d" % merchant_info.merchantId)
    except exc.SQLAlchemyError as e:
        log.error("删除商户相关的所有feedback信息失败！！ ID:%d" % merchant_info.merchantId)

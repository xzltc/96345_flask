from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, render_template
from pyecharts.globals import ThemeType
from pyecharts import options as opts
from pyecharts.charts import Bar
import check_update
import atexit
import fcntl
import tools
import db

db_path = 'sqlite:///96345.db'
param = {"code": "server_content"}
base_url = "http://www.sx96345.com"
header = "/centre/life_service/"

# 日志模块实例化一次，统一使用，保证所有都在root logger下
logger = tools.get_single_logger()

# Flask web端所有功能封装在server中
app = Flask(__name__)


# 默认路由直接渲染主页
@app.route("/")
def index():
    return render_template("index.html")


# ajax获取类目主表路由
@app.route("/barChart/<int:item_id>")
def get_bar_chart(item_id):
    c = item_bar(item_id)
    return c.dump_options_with_quotes()


# 根据类目id获取类目表
def item_bar(item_id) -> Bar:
    logger.debug("显示总表")
    # 创建Session 数据库相关操作
    # engine = create_engine('sqlite:///96345.db', echo=True)
    # Session = sessionmaker(bind=engine)
    # session = Session()
    session = db.get_db_session(db_path)
    # 取得所有当前类目数据库数据 元祖类型 降序
    result = db.query_date_feedback_info(session, item_id, tools.get_assign_year_date(2))
    res = tools.change_2_pyechart_format(result)

    t = (
        Bar(init_opts=opts.InitOpts(theme=ThemeType.WHITE))
            .add_xaxis(res.get('name'))
            .add_yaxis("批评", res.get('cri'), stack="stack1", itemstyle_opts=opts.ItemStyleOpts(color='red'))
            .add_yaxis("满意", res.get('sat'), stack="stack1", itemstyle_opts=opts.ItemStyleOpts(color='#29b394'))
            .add_yaxis("表扬", res.get('pri'), stack="stack1", itemstyle_opts=opts.ItemStyleOpts(color='#fed861'))
            .set_series_opts(label_opts=opts.LabelOpts(is_show=False), )
            .set_global_opts(title_opts=opts.TitleOpts(title="当前概况"),
                             xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=-15)),
                             datazoom_opts=opts.DataZoomOpts()
                             )
    )
    session.close()
    return t


# ajax增量表路由
@app.route("/increaseBarChart/<int:item_id>/<int:day>")
def get_increase_bar_chart(day, item_id):
    c = increase_bar(day, item_id)
    return c.dump_options_with_quotes()


# 增量表
def increase_bar(day, item_id) -> Bar:
    logger.debug("显示增量表")
    # 创建Session 数据库相关操作
    # engine = create_engine('sqlite:///96345.db', echo=True)
    # Session = sessionmaker(bind=engine)
    # session = Session()
    session = db.get_db_session(db_path)
    # 取得所有当前类目数据库数据 元祖类型 降序
    result = tools.get_item_merchants_timelaspes_increase(session, item_id, tools.get_today()
                                                          , tools.get_assign_year_date(day))
    c = (
        Bar()
            .add_xaxis(result.get('name'))
            .add_yaxis("新增单数", result.get('increment'))
            .set_global_opts()
            .set_series_opts(
            label_opts=opts.LabelOpts(is_show=True),
            markpoint_opts=opts.MarkPointOpts(
                data=[
                    opts.MarkPointItem(type_="max", name="最大值"),
                ]
            ),
        )
    )
    session.close()
    return c


# 每天第一次插入  定时任务
def insert_feedback():
    # 创建Session 数据库相关操作
    session = db.get_db_session(db_path)
    logger.info("插入定时任务启动 %s" % str(tools.get_now()))
    check_update.every_day_update_feedback(param, base_url, header, session, 0)
    session.close()


# 每天多次更新操作 定时任务
def update_feedback():
    session = db.get_db_session(db_path)
    logger.info("更新定时任务启动 %s " % str(tools.get_now()))
    # print("更新定时任务启动 ", tools.get_now())
    check_update.every_day_update_feedback(param, base_url, header, session, 1)
    session.close()


def register_scheduler():
    """
    注册定时任务
    """
    sched = BackgroundScheduler(daemon=True)
    # 时区是个大坑 淦 不要搞什么UTC UTC-8 老老实实用本地时间最简单
    sched.add_job(insert_feedback, 'cron', day_of_week='0-6', hour='14', minute='27', id='insert_feedback')
    sched.add_job(update_feedback, 'cron', day_of_week='0-6', hour='8,10,12,13,14,16,18,21,23', minute='24',
                  id='update_feedback')
    f = open("scheduler.lock", "wb")
    # noinspection PyBroadException
    try:
        fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
        sched.start()
        logger.info("定时任务启动成功！")
    except Exception as e:
        logger.error("定时任务启动失败！")

    def unlock():
        fcntl.flock(f, fcntl.LOCK_UN)
        f.close()

    atexit.register(unlock)


# sched = BackgroundScheduler(daemon=True)
# # 时区是个大坑 淦 不要搞什么UTC UTC-8 老老实实用本地时间最简单
# sched.add_job(insert_feedback, 'cron', day_of_week='0-6', hour='14', minute='27', id='insert_feedback')
# sched.add_job(update_feedback, 'cron', day_of_week='0-6', hour='8,10,12,13,14,16,18,21,23', minute='24',
#               id='update_feedback')
# sched.start()
register_scheduler()


if __name__ == "__main__":
    app.run()

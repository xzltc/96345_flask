from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, render_template
from pyecharts.globals import ThemeType
from pyecharts import options as opts
from pyecharts.charts import Bar
from flask_cors import *
import check_update
import atexit
import fcntl
import json
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
CORS(app, supports_credentials=True)


# 默认路由直接渲染主页
@app.route("/")
def index():
    return render_template("index.html")


@app.route('/serve/updateTime')
def get_update_time():
    session = db.get_db_session(db_path)
    res = db.query_all_item(session)
    time = res[7].updateTime
    ret_time = str(time.month) + '-' + str(time.day) + ' ' + str(time.hour) + ':' + str(time.minute)
    dict1 = {'updateTime': ret_time}
    session.close()
    return json.dumps(dict1)


# ajax获取类目主表路由
@app.route("/barChart/<int:item_id>")
def get_bar_chart(item_id):
    c = item_bar(item_id)
    return c.dump_options_with_quotes()


@app.route("/table/<int:item_id>", methods=['GET'])
def get_item_table(item_id):
    session = db.get_db_session(db_path)
    result = db.query_date_feedback_info(session, item_id, tools.get_today())
    formatted_result = tools.change_2_layui_table_formatted(result)
    return json.dumps(formatted_result)


# 根据类目id获取类目表
def item_bar(item_id) -> Bar:
    logger.debug("显示总表")
    # 创建Session 数据库相关操作
    # engine = create_engine('sqlite:///96345.db', echo=True)
    # Session = sessionmaker(bind=engine)
    # session = Session()
    session = db.get_db_session(db_path)
    # 取得所有当前类目数据库数据 元祖类型 降序
    result = db.query_date_feedback_info(session, item_id, tools.get_today())
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
                             datazoom_opts=[opts.DataZoomOpts(range_start=0, range_end=50),  # 设置起始结束范围
                                            opts.DataZoomOpts(type_="inside")]  # 增加内缩放
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
        Bar(init_opts=opts.InitOpts(theme=ThemeType.ROMANTIC))
            .add_xaxis(result.get('name'))
            .add_yaxis("新增单数", result.get('increment'))
            .reversal_axis()
            .set_global_opts(
            datazoom_opts=[opts.DataZoomOpts(range_start=60, range_end=100, orient="vertical"),
                           opts.DataZoomOpts(type_="inside", orient="vertical")],
            tooltip_opts=[opts.TooltipOpts(trigger='axis', axis_pointer_type='shadow')]
        )
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
    sched.add_job(insert_feedback, 'cron', day_of_week='0-6', hour='0', minute='45', id='insert_feedback')
    sched.add_job(update_feedback, 'cron', day_of_week='0-6', hour='8,9,10,11,12,13,15,16,17,18,19,20,21,22',
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


# 注册定时任务
register_scheduler()

if __name__ == "__main__":
    app.run()

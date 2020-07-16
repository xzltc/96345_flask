from flask import Flask, render_template
from pyecharts.commons.utils import JsCode
from pyecharts.globals import ThemeType
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import db
from random import randrange
from pyecharts import options as opts
from pyecharts.charts import Bar
from pyecharts.faker import Faker
import tools

app_test = Flask(__name__)


@app_test.route('/')
def hello_world():
    return 'Hello World!'


@app_test.route('/index')
def index():
    # get_bar_chart()
    return render_template('index.html')


@app_test.route("/barChart/<int:item_id>")
def get_bar_chart(item_id):
    # c = bar_base()
    c = bar_test(item_id)
    return c.dump_options_with_quotes()


@app_test.route("/increaseBarChart")
def get_increase_bar_chart():
    # c = bar_base()
    c = bar_test_two()
    return c.dump_options_with_quotes()


def bar_test_three(day):
    category = 68
    # 创建Session 数据库相关操作
    engine = create_engine('sqlite:///96345.db', echo=True)
    Session = sessionmaker(bind=engine)
    session = Session()
    # 取得所有当前类目数据库数据 元祖类型 降序
    result = tools.get_item_merchants_timelaspes_increase(session, category, tools.get_today(),
                                                          tools.get_assign_year_date(day))

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

    return c


@app_test.route("/increaseBarChart2/<int:day>")
def get_increase_bar_chart2(day):
    # c = bar_base()
    c = bar_test_three(day)
    return c.dump_options_with_quotes()


def bar_test(item_id) -> Bar:
    category = 68
    # 创建Session 数据库相关操作
    engine = create_engine('sqlite:///96345.db', echo=True)
    Session = sessionmaker(bind=engine)
    session = Session()
    # 取得所有当前类目数据库数据 元祖类型 降序
    result = db.query_date_feedback_info(session, item_id, tools.get_today())
    res = tools.change_2_pyechart_format(result)

    t = (
        Bar(init_opts=opts.InitOpts(theme=ThemeType.WHITE))
        .add_xaxis(res.get('name'))
        .add_yaxis("批评", res.get('cri'), stack="stack1", itemstyle_opts=opts.ItemStyleOpts(color='red'))
        .add_yaxis("满意", res.get('sat'), stack="stack1", itemstyle_opts=opts.ItemStyleOpts(color='#29b394'))
        .add_yaxis("表扬", res.get('pri'), stack="stack1", itemstyle_opts=opts.ItemStyleOpts(color='#fed861'))
        .set_series_opts(label_opts=opts.LabelOpts(is_show=False),)
        .set_global_opts(title_opts=opts.TitleOpts(title="当前概况"),
                         xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=-15)),
                         datazoom_opts=opts.DataZoomOpts()
                         )
    )

    return t


def bar_test_two() -> Bar:
    category = 68
    # 创建Session 数据库相关操作
    engine = create_engine('sqlite:///96345.db', echo=True)
    Session = sessionmaker(bind=engine)
    session = Session()
    # 取得所有当前类目数据库数据 元祖类型 降序
    result = tools.get_item_merchants_timelaspes_increase(session, category, tools.get_today(), tools.get_previous_date())

    c = (
        Bar()
        .add_xaxis(result.get('name'))
        .add_yaxis("今日完成单数", result.get('increment'))
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

    return c


def bar_base() -> Bar:
    c = (
        Bar({"theme": ThemeType.MACARONS})
            .add_xaxis(["老许开锁", "培良锁行", "昌昌刻印", "赵建华", "高跟鞋", "袜子"])
            .add_yaxis("满意", [randrange(0, 100) for _ in range(6)])
            .add_yaxis("表扬", [randrange(0, 100) for _ in range(6)])
            .add_yaxis("批评", [randrange(0, 100) for _ in range(6)])
            .set_global_opts(title_opts=opts.TitleOpts(title="Bar-基本示例", subtitle="我是副标题"),
                             # 显示工具栏toolbox
                             # toolbox_opts=opts.ToolboxOpts(),
                             # 数据缩放栏
                             datazoom_opts=opts.DataZoomOpts())
    )

    c2 = (
        Bar()
        # Faker.choose() 测试数据 Faker是pyecharts内置的一个类
        .add_xaxis(Faker.choose())
        .add_yaxis("满意", Faker.values(), stack="stack1")
        .add_yaxis("表扬", Faker.values(), stack="stack1")
        .add_yaxis("批评", Faker.values(), stack="stack1")
        .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
        .set_global_opts(title_opts=opts.TitleOpts(title="Bar-堆叠数据（全部）"),
                         datazoom_opts=opts.DataZoomOpts())
    )
    return c2


@app_test.route('/test')
def echart_test():
    category = 1
    # 创建Session 数据库相关操作
    engine = create_engine('sqlite:///96345.db', echo=True)
    Session = sessionmaker(bind=engine)
    session = Session()
    res = db.query_merchart_detail_info(session, int(category))
    return str(len(res))


@app_test.route('/bar')
def bar():
    r = 1


# if __name__ == '__main__':
#     app.run()

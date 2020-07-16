from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from entity import Item, Merchant, Feedback
from bs4 import BeautifulSoup
import requests
import numpy as np
import re
import db
import tools

log = tools.get_single_logger()  # 日志模块


def main():
    # 爬取网址
    category = "1"  # 不同的服务对应不同的类目 68=开锁换锁
    db_path = 'sqlite:///96345.db'
    param = {"code": "server_content"}
    base_url = "http://www.sx96345.com"
    header = "/centre/life_service/"  # url后面跟着的一点
    session = db.get_db_session(db_path, True)

    all_service_info = get_all_pages_service_info(base_url, header, param, category)
    all_service_info_detail = get_personal_service_data(all_service_info)

    # db.insert_merchant(session, all_service_info)
    # db.insert_feedback(session, all_service_info_detail)

    # res = db.query_merchant_info(session, int(category))

    # res = db.query_date_feedback_info(session, int(category), tools.get_pervious_date())
    # print(res)


# 获取指定服务类目中的所有商户粗略信息，不含反馈信息
def get_all_pages_service_info(base_url, header, param, category):
    dataList = []  # 所有数据列表
    target = base_url + header + category

    # 按照页面进行遍历爬取
    for p in range(1, 10):
        param['page'] = str(p)  # 拼接上页号
        r = ask_URL(target, param)
        soup = BeautifulSoup(r.text, 'html.parser')
        a_lists = soup.find('div', class_="merchant_r_list").select("ul>li>a")
        if a_lists:  # ul中是否有数据判断是不是尾页
            for item in a_lists:
                entity = {}
                # 获取每个tag中商户名称和地址，生成字典放入dataList中
                service_site = base_url + item.attrs.get("href")
                service_name = re.sub("\\(.*\\)|\（.|\）", "", item.get_text())  # 去括号
                service_name = re.sub("—|-.*", "", service_name)  # 去-后字符信息
                service_id = int(re.search("(?<=show/).*?(?=\?)", service_site).group())  # 正则匹配拿id

                if len(service_name) == 0:
                    service_name = item.get_text()
                service_name = service_name.replace("(本）", "").replace("(个人)", "")
                entity['id'] = service_id
                entity['name'] = service_name
                entity['href'] = service_site
                entity['item'] = category
                dataList.append(entity)
                log.debug(entity)
        else:
            log.info("---总页号数为---：%d" % (p - 1))
            # print("总页号数为：", p - 1)
            break
    log.debug("---总商户数为：%d---" % (len(dataList)))
    # print("总商户数为：", len(dataList))
    # 输出结果
    return dataList


# 爬取商户的详细信息，包含反馈信息
def get_personal_service_data(all_info):
    personal_service_data = []  # 所有详细信息字典列表

    for i in all_info:
        lists = {}  # 当前商家详细信息
        service_name = i.get('name')
        base_url = i.get('href')  # 获取商户详情页地址
        service_id = int(re.search("(?<=show/).*?(?=\?)", base_url).group())  # 正则匹配拿id

        # 取得对象
        r = ask_URL(base_url)
        soup = BeautifulSoup(r.text, 'html.parser')
        p_info = soup.find_all('span', class_='praise')

        # 获取满意 表扬 批评
        satisfaction_num = int(p_info[0].find('em').get_text())  # 满意
        praise_num = int(p_info[1].find('em').get_text())  # 表扬
        criticism_num = int(p_info[2].find('em').get_text())  # 批评
        amount = satisfaction_num + praise_num + criticism_num  # 总数

        # 写入字典
        lists['id'] = service_id
        lists['name'] = service_name
        lists['href'] = base_url
        lists['item'] = i.get('item')
        lists['satisfaction'] = satisfaction_num
        lists['praise'] = praise_num
        lists['criticism'] = criticism_num
        lists['amount'] = amount

        # append到返回列表中
        personal_service_data.append(lists)
    for ii in personal_service_data:  # 测试输出用
        log.debug(ii)
    return personal_service_data


# 得到指定网页内容 return response对象
def ask_URL(url, param={}, time=20):
    # 附加头，模拟浏览器访问
    header = {"content-type": "application/json",
              "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) "
                            "Chrome/83.0.4103.116 Safari/537.36 Edg/83.0.478.56"}
    try:
        r = requests.get(url, params=param, headers=header, timeout=time)
        # log.debug(r.url)
        # 访问是否为正常状态
        if r.status_code == 200:
            return r
        else:
            log.error('Get Page Failed %d' % r.status_code)
            return None
    # 访问超时异常处理
    except requests.exceptions.Timeout:
        log.error("连接超时！")
    except requests.exceptions as e:
        log.error(e)


# 主函数
if __name__ == '__main__':
    main()

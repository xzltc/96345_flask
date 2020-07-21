from sqlalchemy.ext.declarative import declarative_base
import datetime
from sqlalchemy import create_engine, Column, Integer, Text, Date, DateTime

# Base基类
Base = declarative_base()


# 定义映射类Item，其继承上一步创建的Base，一个类就是一个数据库表
class Item(Base):
    # 指定本类映射到users表
    __tablename__ = 'item'

    # 指定id映射到id字段; id字段为整型，为主键
    id = Column(Integer, primary_key=True, unique=True)
    # 指定name映射到name字段; name字段为字符串类形，Text是不定长字符串
    serviceName = Column(Text, nullable=False)
    serviceAmount = Column(Integer, nullable=False)
    # DateTime数据类型和sqlite3类型相符合    Python datetime => sqlite DATETIME 才能写入
    updateTime = Column(DateTime, default=datetime.datetime.now(), nullable=True)

    # object 基类也存在该方法，这里重写该方法
    # _repr_方法默认返回该对象实现类的“类名+object at +内存地址”值
    def __repr__(self):
        return "<Item[id='%s', serviceName='%s', serviceAmount='%s', updateTime='%s']>" % (
            self.id, self.serviceName, self.serviceAmount, self.updateTime)


class Feedback(Base):
    __tablename__ = 'feedback'

    id = Column(Integer, primary_key=True, autoincrement=True)
    merchantId = Column(Integer, nullable=False)
    itemId = Column(Integer, nullable=False)
    satisfaction = Column(Integer, nullable=False)
    praise = Column(Integer, nullable=False)
    criticism = Column(Integer, nullable=False)
    amount = Column(Integer, nullable=False)
    createTime = Column(Date, default=datetime.date.today(), nullable=False)

    def __repr__(self):
        return "<feedback[merchantId='%s', satisfaction='%s', praise='%s', criticism='%s' , amount='%s' , createTime='%s']>" % (
            self.merchantId, self.satisfaction, self.praise, self.criticism, self.amount, self.createTime)


class Merchant(Base):
    __tablename__ = 'merchant'

    id = Column(Integer, primary_key=True, autoincrement=True)
    merchantId = Column(Integer, nullable=False)
    itemId = Column(Integer, nullable=False)
    merchantName = Column(Text, nullable=False)
    href = Column(Text, nullable=False)

    def __repr__(self):
        return "<merchant[id='%s', merchantId='%s' , itemId='%s' ,merchantName='%s', href='%s']>" % (
            self.id, self.merchantId, self.itemId, self.merchantName, self.href)

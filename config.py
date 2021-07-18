import os


# 获取当前 config.py文件的系统绝对路径
basedir = os.path.abspath(os.path.dirname(__file__))


# 基础配置
class BasicConfig(object):

    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'todoism.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

# 开发环境, 依赖基础配置
class DevelopmentConfig(BasicConfig):
    pass


# 生产环境, 依赖基础配置
class ProductionConfig(BasicConfig):
    pass


# 测试环境
class TestingConfig(BasicConfig):
    pass

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig
}
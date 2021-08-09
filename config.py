import os

basedir = os.path.abspath(os.path.dirname(__file__))


class BaseConfig(object):
    SECRET_KEY = 'adfDG DH lkja sdfpoja s df'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'wggglggg-todoism.data')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # babel 配置
    TODOISM_LOCALES = ['en_US', 'zh_Hans_CN']
    TODOISM_DEFAULT_LOCALE = TODOISM_LOCALES[0]  # 当get_locale返回为None时才启用默认的locale为 en_US美国英语



class DevelopmentConfig(BaseConfig):
    pass


class ProductionConfig(BaseConfig):
    pass


class TestingConfig(BaseConfig):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///'
    WTF_CSRF_ENABLED = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
}
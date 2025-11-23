import os
from dotenv import load_dotenv      #导入环境变量的管理模块

load_dotenv()       #加载.env文件中的环境变量

class DatabaseConfig:
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = int(os.getenv("DB_PORT", "5432"))     #注意int，PostgreSQL默认是5432
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_NAME = os.getenv("DB_NAME", "my_app")
    PROJECT_NAME = os.getenv("PROJECT_NAME", "MY_PROJECT")

    @property       #Python装饰器，将方法变成属性,可以像访问属性一样调用方法：db_config.DATABASE_URL
    def DATABASE_URL(self):             #注意有self（@property 创建的是实例方法）
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"   #默认端口会省略

db_config = DatabaseConfig()


#property 所有物，财产权
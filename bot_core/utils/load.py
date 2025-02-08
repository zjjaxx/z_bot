import os
import importlib
def load_modules(dirName:str='strategies'):
        modules=[]
        # 查找目录下所有文件
        strategies = os.listdir(dirName)
        # 过滤__init__.py
        strategies = filter(lambda file: file.endswith('.py') and file != '__init__.py', strategies)
        for strategy_file in strategies:
            # 去除后缀名
            strategy_module_name = os.path.basename(strategy_file)[:-3]
            # 加载模块
            module=importlib.import_module('.' + strategy_module_name, dirName)
            modules.append(module)
        return modules
from setuptools import setup, find_packages
from setuptools.command.install import install
import os
import sys
import subprocess

class CustomInstall(install):
    def run(self):
        install.run(self)
        self._setup_path()
    
    def _setup_path(self):
        # 获取脚本安装路径
        script_dir = os.path.expanduser("~/Library/Python/3.9/bin")
        
        # 检测当前 shell
        shell = os.environ.get('SHELL', '/bin/zsh')
        
        if 'zsh' in shell:
            config_file = os.path.expanduser("~/.zshrc")
        elif 'bash' in shell:
            config_file = os.path.expanduser("~/.bash_profile")
        else:
            config_file = os.path.expanduser("~/.profile")
        
        # 检查 PATH 是否已配置
        path_line = f'export PATH="{script_dir}:$PATH"'
        
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    content = f.read()
                    if script_dir in content:
                        print(f"\n✅ PATH 已配置，无需修改")
                        return
            
            # 自动添加 PATH
            with open(config_file, 'a') as f:
                f.write(f"\n# jgy CLI 自动配置\n{path_line}\n")
            
            print(f"""
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║   🎉 金谷园饺子馆 CLI 安装成功！                          ║
║                                                          ║
║   ✅ 已自动配置环境变量                                   ║
║                                                          ║
║   请运行以下命令使配置生效：                               ║
║                                                          ║
║   source {config_file}                                   ║
║                                                          ║
║   然后就能使用：jgy --help                                 ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
""")
        except Exception as e:
            print(f"""
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║   🎉 金谷园饺子馆 CLI 安装成功！                          ║
║                                                          ║
║   ⚠️  自动配置失败，请手动运行：                          ║
║                                                          ║
║   echo 'export PATH="{script_dir}:$PATH"' >> {config_file}
║   source {config_file}                                   ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
""")

setup(
    name="jgy",
    version="0.1.3",
    description="金谷园饺子馆 - 命令行查询工具",
    author="金谷园",
    packages=find_packages(),
    install_requires=[
        "click>=8.0",
        "rich>=13.0",
    ],
    cmdclass={
        'install': CustomInstall,
    },
    entry_points={
        "console_scripts": [
            "jgy=jingu_yuan.cli:main",
        ],
    },
    python_requires=">=3.8",
    include_package_data=True,
    package_data={
        "jingu_yuan": ["data/*.json", "game/*.html"],
    },
)

## TA-Lib centos 部署

```
wget https://github.com/ta-lib/ta-lib/releases/download/v0.6.4/ta-lib-0.6.4-src.tar.gz
tar -xzf ta-lib-0.6.4-src.tar.gz
cd ta-lib-0.6.4/
./configure --prefix=/usr
make
sudo make install
```

```
pip3 install TA-Lib
```
若Python包安装失败，确保/usr/lib在库路径中，可尝试：
```
export LD_LIBRARY_PATH=/usr/lib:$LD_LIBRARY_PATH
sudo ldconfig
```

## 部署命令

```
pip3 install gunicorn

gunicorn --bind unix:/tmp/47.92.125.144.socket z_bot.wsgi:application
```

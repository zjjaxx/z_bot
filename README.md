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

## sqlite3升级
### 卸载旧版本（慎用！）
```
sudo yum remove sqlite -y
```

### 安装编译依赖
```
sudo yum groupinstall 'Development Tools' -y
sudo yum install tcl wget -y
```

# 下载最新版（以 3.45.2 为例）
```
wget https://www.sqlite.org/2024/sqlite-autoconf-3450200.tar.gz
tar xzvf sqlite-autoconf-3450200.tar.gz
cd sqlite-autoconf-3450200
```

# 编译安装
```
./configure --prefix=/usr/local --disable-static --enable-fts5
make -j $(nproc)
sudo make install
```

# 更新库链接
```
echo '/usr/local/lib' | sudo tee /etc/ld.so.conf.d/sqlite.conf
sudo ldconfig
```

# 验证版本
```
/usr/local/bin/sqlite3 --version  # 应显示 3.45.2
```

# pjsip 编译准备
1. sudo apt-get install python-dev
2. apt-get install libasound2-dev
3. apt-get install gcc
4. apt-get install g++
5. apt-get install make

# pjsip源码获取
1. Download pjsip 2.6 from http://www.pjsip.org/   （咱们内网服务器上有2.6的压缩包，官网目前是2.7了，最好用2.6）
2. tar   -jxvf    xx.tar.bz2

# pjsip编译 (参考https://trac.pjsip.org/repos/wiki/Python_SIP/Build_Install)
1. cd 到解压缩后的pjsip源码目录
2. ./configure CFLAGS='-fPIC'
3. make dep
4. make 
5. Go to pjsip-apps/src/python directory
6. sudo python ./setup.py install


# 其他依赖
- 本地需要有python2、python3运行环境
  - python2 > 2.7.1
  - python3 > 3.6.1
- 安装python2和python3的依赖
  pip install -r py2requirment.txt
  pip3 install -r py3requirment.txt
- 配置uc.cfg
- python sipua_manager


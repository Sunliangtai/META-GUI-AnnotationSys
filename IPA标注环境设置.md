### IPA标注环境设置

### 安装python

安装Anaconda3-2021.05-Windows-x86_64.exe，选择默认的设置就好。取决于具体的电脑配置，该过程可能需要几分钟或者十几分钟。

### 安装adb

进入代码文件夹的`code\platform-tools_r31.0.3-windows\platform-tools`, 里面有adb的执行文件，我们需要把这个目录添加到环境变量中。

修改环境变量的方式：

1. 在系统搜索框搜索环境变量，出现

![image-20211010230343454](C:\Users\galaxy\AppData\Roaming\Typora\typora-user-images\image-20211010230343454.png)

后点击打开。

2. 点击环境变量这个按钮

![image-20211010230456011](C:\Users\galaxy\AppData\Roaming\Typora\typora-user-images\image-20211010230456011.png)

3. 在出现的这个页面中，双击path

![image-20211010230535021](C:\Users\galaxy\AppData\Roaming\Typora\typora-user-images\image-20211010230535021.png)

4. 在出现的界面中，点击新建，然后点击浏览：

![image-20211010230625259](C:\Users\galaxy\AppData\Roaming\Typora\typora-user-images\image-20211010230625259.png)

5. 选择你解压后的platform-tools目录然后确定

![image-20211010234911620](C:\Users\galaxy\AppData\Roaming\Typora\typora-user-images\image-20211010234911620.png)



添加完后，按照如下的方式验证是否成功：

打开anaconda powershell prompt（系统搜索框搜索anaconda powershell prompt (anaconda3)然后回车打开），

![image-20211011111431989](C:\Users\galaxy\AppData\Roaming\Typora\typora-user-images\image-20211011111431989.png)

输入`adb version ，如果出现类似于下面的文字可以找得到命令那就ok了

![image-20211010235109818](C:\Users\galaxy\AppData\Roaming\Typora\typora-user-images\image-20211010235109818.png)

### 连接手机

确保adb安装好后，打开手机，连接好usb数据线，打开prompt或者cmd，输入`adb devices`，手机屏幕上会出现一个“allow usb debugging?”的提示框，选择ok

如果没有发现这个提示框就插拔一下再来一次。如果列出来有类似于

![image-20211004114908138](C:\Users\galaxy\AppData\Roaming\Typora\typora-user-images\image-20211004114908138.png)

这样子的信息那就说明成功了

### 启动代码

1. 安装好依赖。

2. 打开anaconda powershell prompt，复制你的解压文件夹的路径，输入

   `cd C:\Users\galaxy\Desktop\code`（后面那一串换成你的实际路径）

   就可以进入代码文件夹。

3. 复制以下内容到anaconda promt, 回车

`pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple`

![image-20211011074133852](C:\Users\galaxy\AppData\Roaming\Typora\typora-user-images\image-20211011074133852.png)

4. 输入`pip install -r requirement.txt`， 回车

### 以下内容每次启动系统都要执行一次

### 连接手机

确保adb安装好后，打开手机，连接好usb数据线，打开prompt或者cmd，输入`adb devices`，手机屏幕上会出现一个“allow usb debugging?”的提示框，选择ok

如果没有发现这个提示框就插拔一下再来一次。如果列出来有类似于

![image-20211004114908138](C:\Users\galaxy\AppData\Roaming\Typora\typora-user-images\image-20211004114908138.png)

这样子的信息那就说明成功了



1. 进入代码文件夹: `cd C:\Users\galaxy\Desktop\code`（后面那一串换成你的实际路径）,回车
2. 启动代码，输入`python server.py`，回车
3. 打开浏览器输入`http://127.0.0.1:5000/#dialog`, 如果能够正常打开和获取截图就说明一切正常


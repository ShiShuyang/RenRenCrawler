# RenRenCrawler
人人网状态保存。万一它哪天倒闭了，能保存自己的回忆。
python2版本不再更新。

2018/11/16 更新python3版本。可以爬取状态、日志、相册照片，并且保存下面的回复。
需要新建一个cookie.txt，在自己登陆人人后把自己的cookies复制进去。

目前已知问题：
①对超过100条的回复没有进一步处理（即一个状态、日志或相册的回复只显示前100条），高兴了再改。
②一个相册的总回复没有爬取，高兴了再改。

使用方法：

在https://github.com/ShiShuyang/RenRenCrawler/releases 中下载reren.exe，然后在相同文件夹下新建一个cookie.txt，如下图。
![Image text](https://raw.githubusercontent.com/ShiShuyang/RenRenCrawler/master/1.png)
登录自己的人人账号，在浏览器中按F12，选择网络（绿色方框），然后刷新页面。在网络下会显示一堆东西。找到红色圆圈的文件并点击（文件名和你人人ID相同），找到右侧cookies，把选中内容复制下载，粘贴到cookie.txt中。如下图所示：
![Image text](https://raw.githubusercontent.com/ShiShuyang/RenRenCrawler/master/2.png)
然后双击renren.exe运行，效果如下如所示：
![Image text](https://raw.githubusercontent.com/ShiShuyang/RenRenCrawler/master/3.png)

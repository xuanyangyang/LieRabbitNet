# LieRabbitNet
远程操控，调用shell，上传文件，执行命令
=======
Windows Linux都可以<br>
use python3.x<br>

使用方法：<br>
python3 lierabbitnet.py -t target_host -p port<br>
-l --listen              - listen on [host]:[post] for incoming connections<br>
-c --command             - initialize a command shell<br>
-u --upload=destination  - upon receiving connection upload a file and write to [destination]<br>
-f --file=filename       - upload a file<br>


演示：
在目标上：<br>
python3 lierabbitnet.py -l -c -p 9999  #启动<br>

在本机上：<br>
python3 lierabbitnet.py -t 目标ip -p 9999<br>
进行各种操作<br>
![img](https://github.com/LieRabbit/LieRabbitNet/blob/master/images/1.jpg)
![img](https://github.com/LieRabbit/LieRabbitNet/blob/master/images/2.jpg)
![img](https://github.com/LieRabbit/LieRabbitNet/blob/master/images/3.jpg)
![img](https://github.com/LieRabbit/LieRabbitNet/blob/master/images/4.jpg)
运行一系列命令后：<br>
![img](https://github.com/LieRabbit/LieRabbitNet/blob/master/images/5.png)




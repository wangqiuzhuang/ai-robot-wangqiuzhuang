# wangqiuzhuang's 10th week's homework description  
## 本周概览  
- 使用 docker run -v 进行本地目录挂载  power shsell退出,则本地和远端的虚拟连接断开,如果连接成功,操作本地文件会在远端也进行相应的操作,比如本地新增一个text.txt文件,则远端也会生成;目的就是方便本地操作远端文件,即便远端文件误删除,本地也存在对应的文件;  
 ![alt text](img/本地远程文件夹绑定-1.png)
- 本地创建一个py文件验证远程也出现对应的文件
![alt text](img/本地新增py文件验证远端也会出现相应文件.png)  
- 远程运行对应的文件  成功  
![alt text](img/远端执行py文件发现成功.png)  

- 下载git远程cat代码,https://github.com/ndb796/Python-Data-Analysis-and-Image-Processing-Tutorial/blob/master/06.%20OpenCV%20%EC%86%8C%EA%B0%9C%20%EB%B0%8F%20%EA%B8%B0%EB%B3%B8%20%EC%82%AC%EC%9A%A9%EB%B2%95/OpenCV%20%EC%86%8C%EA%B0%9C%20%EB%B0%8F%20%EA%B8%B0%EB%B3%B8%20%EC%82%AC%EC%9A%A9%EB%B2%95.ipynb  
![alt text](img/下载cat代码.png)
- 运行py文件出现小猫图像  
![alt text](img/出现小猫图片.png)
- 注意执行过程中可能出现版本不兼容的情况   可以问下claude code将 NumPy 版本降级为1.* ,缺少 pybullet 模块 ,可以自己用指令安装.本地缺失图片可以自己在Google下载一个小猫图片.

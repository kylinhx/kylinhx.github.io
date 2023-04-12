---
title: DFT的算法比较
tags: [Code,Matlab]
mathjax: true
categories: Study
---

# 	DFT的直接计算与快速算法比较

git：[Degital_Singal_Process/DFT_Compare at main · kylinhx/Degital_Singal_Process (github.com)](https://github.com/kylinhx/Degital_Singal_Process/tree/main/DFT_Compare)

## 一、实验内容

​			用MATLAB的m语言编写程序，实现基2-FFT（注意不允许采用 MATLAB 系统自带的FFT库函数）。预先分别随机产生一个N=1024点和一个N=4096点的复数序列存储备用，作为傅里叶变换的输入数据

## 二、实验要求

1. 直接计算N点DFT，输出计算结果
2. 采用所设计的FFT程序，输出计算结果
3. 使用MATLAB的FFT程序，输出计算结果。对三者的输出结果进行比较
4. 采用多次运行取平均的方法计算三种傅里叶变换算法下计算 N=1024 和 N=4096 点DFT所需的时间，并进行比较

## 三、实验环境

​			MATLAB R2021b

## 四、实验过程

​			step1：编写脚本随机产生N=1024点和N=4096点的复数序列X1，X2

​			step2：编写程序实现基2-FFT、DFT直接运算

​			step3：计算N点DFT、编写的FFT程序、MATLAB自带的FFT程序对N=1024点和N=4096点DFT进行比较

​			step4：采用多次运行取平均的方法计算三种傅里叶变换算法下计算 N=1024 和 N=4096 点DFT所需的时间，并进行比较

### step1：代码展示，以及代码运行截图

​		N1024.m

```matlab
%N=1024复数随机序列生成
M = 1024;
K = 1;
W= rand(M,K)+1i*rand(M,K);
X1 = W'
```

​		N4096.m

```matlab
% N=4096复数随机序列生成
M = 4096;
K = 1;
W= rand(M,K)+1i*rand(M,K);
X2=W'
```

​		运行结果截图![](image-20221120152835483.png)

### step2：代码展示及运行截图展示

基2-FFT主要实现下图运算：

![](image-20221105225434371.png)

基2-FFT运算函数

​		DIT_FFT_2_MOD.m

```matlab
function [Xk]=DIT_FFT_2_MOD(xn,N)
    t=1:N;
    WWr=exp(-1i*2*pi/N*[0:N/2-1].'); %旋转因子
    %蝶形运算开始
    M=log2(N);%“级”的数量
    % 码位倒置
    Xk=permute(reshape(xn,2*ones(1,M)),M:-1:1);
    Xk=Xk(:);
    N2=N/2;
    Num_of_Group=N2;%每一级中组的个数初始值
    Interval_of_Group=1;%每一级中组与组之间的间距

    for m=0:M-1 %“级”循环开始
        Wr=WWr(1:Num_of_Group:end);
        gMatrix2=reshape(t,Interval_of_Group,2,Num_of_Group);
        gMatrix21=reshape(gMatrix2(:,1,:),N2,1);
        gMatrix22=reshape(gMatrix2(:,2,:),N2,1);
        if(m==0)
            XKtemp=Xk(gMatrix22);%第0级，蝶形运算式
        elseif(m==1)
            XKtemp=Xk(gMatrix22);
            XKtemp(2:2:end)=XKtemp(2:2:end)*Wr(2);%第1级，蝶形运算式
        else
            ss=repmat(Wr,Num_of_Group,1);
            XKtemp=Xk(gMatrix22).*ss;%第m级，第g组的蝶形运算式1
        end
        Xk(gMatrix22)=Xk(gMatrix21)-XKtemp;%第m级，蝶形运算式
        Xk(gMatrix21)=Xk(gMatrix21)+XKtemp;
        Interval_of_Group=Interval_of_Group*2;  %递推
        Num_of_Group=Num_of_Group/2;  %递推
    end
end
```

直接计算DFT       

​		MDFT.m

```matlab
function [Xk]=MDFT(xn,N)
%此函数使用DFT矩阵方法计算序列x(n)的N点DFT
M=length(xn);%记录序列x(n)初始长度
    if M<N   %如果序列长度小于N，补零到N，否则，截取前N项 
        xn=[xn,zeros(1,N-M)];
    else
        xn=xn(:,1:N);  %截取（全部行）前N列 
    end
n=0:N-1; k=0:N-1;      %匹配矩阵维度n,k
W_N=exp(-1i*2*pi/N);   %生成N点DFT对应的旋转因子W(常数)
nk=n'*k;               %生成旋转因子W的幂次系数矩阵(N*N)
W=W_N.^nk;             %生成N点DFT矩阵(N*N),数幂运算
Xk=W*xn';              %[X(k)]=[W]*[x(n)]T,矩阵乘法
Xk=Xk';                %以行向量的方式输出[X(k)]
end
```

### step3、代码展示及运行截图展示

​		DFT_test.m

```matlab
xn1024=X1;
xn4096=X2;
X2_fft_1024=DIT_FFT_2_MOD(xn1024,1024)';    %编写的算法计算1024点FFT
X2_fft_4096=DIT_FFT_2_MOD(xn4096,4096)';    %编写的算法计算4096点FFT

x_fft_1024=fft(xn1024,1024);        %matlab自带的fft计算1024点FFT
x_fft_4096=fft(xn4096,4096);        %matlab自带的fft计算4096点FFT


x_DFT_1024 = MDFT(xn1024,1024);     %直接计算1024点DFT
x_DFT_4096 = MDFT(xn4096,4096);     %直接计算4096点DFT


```

​		运行结果展示：

![](image-20221120153443274.png)

```matlab
x_DFT_1024  %直接计算1024点DFT
x_DFT_4096  %直接计算4096点DFT

x_fft_1024	%直接计算1024fft
x_fft_4096	%直接计算4096fft

X2_fft_1024	%基2—fft 1024点fft
X2_fft_4096 %基2—fft 4096点fft

%结果
```

### step4、代码展示及运行截图展示

**计算结果比较：**

​		pre1024.m

```matlab
Xk1=x_fft_1024;    %计算xn的1024点DFT
%以下为绘图部分
k=0:1023;wk=2*k/1024;      
subplot(3,2,1);stem(wk,abs(Xk1),'.'); 
title('(fft)1024点DFT的幅频特性图');xlabel('ω/π');ylabel('幅度');
subplot(3,2,2);stem(wk,angle(Xk1),'.'); 
line([0,2],[0,0]);title('(fft)1024点DFT的相频特性图')
xlabel('ω/π');ylabel('相位');axis([0,2,-3.5,3.5]);
hold;

Xk2=x_DFT_1024;
k=0:1023;wk=2*k/1024;      
subplot(3,2,3);stem(wk,abs(Xk2),'.'); 
title('(DFT)1024点DFT的幅频特性图');xlabel('ω/π');ylabel('幅度');
subplot(3,2,4);stem(wk,angle(Xk1),'.'); 
line([0,2],[0,0]);title('(DFT)1024点DFT的相频特性图')
xlabel('ω/π');ylabel('相位');axis([0,2,-3.5,3.5]);
hold;

Xk3=X2_fft_1024;
k=0:1023;wk=2*k/1024;      
subplot(3,2,5);stem(wk,abs(Xk3),'.'); 
title('(2-fft)1024点DFT的幅频特性图');xlabel('ω/π');ylabel('幅度');
subplot(3,2,6);stem(wk,angle(Xk1),'.'); 
line([0,2],[0,0]);title('(2-fft)1024点DFT的相频特性图')
xlabel('ω/π');ylabel('相位');axis([0,2,-3.5,3.5]);
hold;
```

![](image-20221120172006699.png)

pre4096.m

```matlab
Xk11=x_fft_4096;    %计算xn的1024点DFT
%以下为绘图部分
k=0:4095;wk=2*k/4096;      
subplot(3,2,1);stem(wk,abs(Xk11),'.'); 
title('(fft)4096点DFT的幅频特性图');xlabel('ω/π');ylabel('幅度');
subplot(3,2,2);stem(wk,angle(Xk11),'.'); 
line([0,2],[0,0]);title('(fft)4096点DFT的相频特性图')
xlabel('ω/π');ylabel('相位');axis([0,2,-3.5,3.5]);
hold;

Xk22=x_DFT_4096;
k=0:4095;wk=2*k/4096;      
subplot(3,2,3);stem(wk,abs(Xk22),'.'); 
title('(DFT)4096点DFT的幅频特性图');xlabel('ω/π');ylabel('幅度');
subplot(3,2,4);stem(wk,angle(Xk22),'.'); 
line([0,2],[0,0]);title('(DFT)4096点DFT的相频特性图')
xlabel('ω/π');ylabel('相位');axis([0,2,-3.5,3.5]);
hold;

Xk33=X2_fft_4096;
k=0:4095;wk=2*k/4096;      
subplot(3,2,5);stem(wk,abs(Xk33),'.'); 
title('(2-fft)4096点DFT的幅频特性图');xlabel('ω/π');ylabel('幅度');
subplot(3,2,6);stem(wk,angle(Xk33),'.'); 
line([0,2],[0,0]);title('(2-fft)4096点DFT的相频特性图')
xlabel('ω/π');ylabel('相位');axis([0,2,-3.5,3.5]);
hold;
```

![](image-20221120172413428.png)

可以看到fft与2-fft在计算结果上与dft有差异，但是差的不多

**计算速度比较：**

​		time_compare.m

```matlab
t1=clock
for index = 0:100
    X2_fft_1024=DIT_FFT_2_MOD(xn1024,1024)';   %2-fft计算1024点FFT
end
t2=clock;
time2_fft_1024(end+1)=etime(t2,t1)

t1=clock
for index = 0:1
    x_DFT_1024 = MDFT(xn1024,1024);           %直接计算1024点DFT
end
t2=clock
time_DFT_1024(end+1)=etime(t2,t1)

t1=clock
for index = 0:1000
    x_fft_1024=fft(xn1024,1024);              %matlab自带1024点FFT
end
t2=clock
time_fft(end+1)=etime(t2,t1)
```

​		经过反复尝试，在dft取1次，fft取1000次，2-fft取100次，结果比较好

​		tcomp.m

```matlab
x=1:100
time2_fft_1024=[]
time_fft=[]
time_DFT_1024=[]
for index=1:100
    time_compare
end
subplot(3,1,1)
plot(x,time_DFT_1024,'red');
xlabel('次数');ylabel('DFT时间');
subplot(3,1,2)
plot(x,time_fft,'blue');
xlabel('次数');ylabel('fft时间');
subplot(3,1,3)
plot(x,time2_fft_1024,'green');
xlabel('次数');ylabel('2-fft时间');

```

![](image-20221120170153725.png)

可以看到，matlab自带的fft算的很快，直接计算DFT很慢，2-fft速度比DFT快很多，但是也没有matlab自带的fft算法快

平均值如下：

```
%matlab自带fft计算1024点DFT： 5.3000e-06
%直接计算1024点DFT： 0.5879
%编写的2-fft计算1024点DFT：4.5960e-04
```


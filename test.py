import numpy as np
import pandas as pd
import csv
import random

csv_file = open('D:/扇区关系.csv', encoding='UTF-8')
full_date = []  # 创建列表准备接收csv各行数据
csv_reader_lines = csv.reader(csv_file)  # 逐行读取csv文件
out = []
row_num = 0
station_num = 0
station_row = 0
print('导入数据开始：导入进度')
for one_line in csv_reader_lines:
    full_date.append(one_line)  # 将读取的csv分行数据按行存入列表‘date’中
    if row_num % 10000 == 0:
        print(row_num)
    row_num = row_num + 1  # 统计行数
print('导入完毕')
print('=====================================')


full_date = np.array(full_date)
out = np.array(out)
full_date = np.insert(full_date, 7, np.zeros(full_date.shape[0], dtype=int), axis=1)  # 输入物理站的天线列表，增加结果标识
full_date = np.insert(full_date, 7, np.zeros(full_date.shape[0], dtype=int), axis=1)  # 输入物理站的天线列表，增加扇区标识
full_date = np.insert(full_date, 7, np.zeros(full_date.shape[0], dtype=int), axis=1)  # 输入物理站的天线列表，增加扇区宽度标识


def dist(x,y):  # 比较角度间的距离
    distout=min(abs(x-y),abs(x+360-y),abs(x-360-y))
    return distout

def randctr(x): # 随机生成中心角度
    antlist=np.int_(x[:,6])
    antgroupcount = np.unique(antlist).shape[0]
    anttolist=np.unique(antlist).tolist()
    fancount=int(x[0,13])
    if antgroupcount > fancount:
        out = random.sample(anttolist,fancount)
        out = np.array(out)
        out = np.sort(out)
    else:
        out = np.array(anttolist)
        out = np.sort(out)
    # print(out)
    return out

def kmeans(y):
    x=np.copy(y)
    # print('======开始KMEAN==========')
    fan_count=int(x[0,13])
    ant_count = int(x.shape[0])
    antlist = np.int_(x[:, 6])
    antgroupcount = np.unique(antlist).shape[0] # 如果去重后天线方向角度小于最大扇区数，将最大扇区数改为天线方向角度去重
    if antgroupcount < fan_count:
        fan_count = antgroupcount
    # print(fan_count,ant_count)
    lossmin=10000
    mm=0
    while mm<30:
        fanctr = randctr(x)
        nn=0
        while nn < 30:
            fandist = np.zeros(fan_count,dtype=float)
            i=0
            while i<ant_count:
                j=0
                while j< int(fanctr.shape[0]):
                    fandist[j]=dist(fanctr[j],int(x[i][6]))
                    j=j+1
                fandistlist=fandist.tolist()
                fandistlist=list(map(int, fandistlist))
                x[i,7]=min(fandistlist)       #距离中心点标准差
                x[i,8]=int(fandistlist.index(min(fandistlist)))  #扇区编号
                i=i+1
            j=0
            while j<fanctr.shape[0]:
                outx=np.where(np.float_(x[:,8]) ==j)
                outy=(x[outx,6]).astype(np.int)
                if outy.size==0:
                    break
                outmean = np.mean(outy)
                fanctr[j] = outmean
                j = j + 1
            loss = np.int_(x[:, 7])
            if loss.shape[0] >1:
                loss = sum(loss)
            else:
                loss = int(loss)
            nn=nn+1
        if loss<lossmin:
            temp = np.copy(x)
            lossmin=loss

        mm=mm+1
    return temp




def verify_min(x):  # 如同频进入一个扇区，则输出错误
    df = pd.DataFrame(x)
    df.columns = ['物理站名', '天线名称', '地市', '使用频段', '经度', '纬度', '小区方向角', '扇区宽度', '扇区编号', '是否有问题', '天线高度', '机械下倾角', '电下倾角',
                  '最大扇区数']
    max_freq = np.max(df.groupby(["扇区编号", "使用频段"])["使用频段"].count())
    if max_freq > 1:
        return 1
    elif max_freq == 1:
        return 0


def verify_max(x, y):  # 如扇区编号大于 最大同频天线数则增加扫描步长
    if int(x[0, 13]) >= y:
        return 0
    elif int(x[0, 13]) < y:
        return 1

def main(x):
    y=kmeans(x)
    ver_min=verify_min(y)
    if ver_min==1:
        y[:,9]=1
    df = pd.DataFrame(y)
    df.to_csv("test.csv", mode='a', index=False, encoding='utf_8_sig', header=0, sep=',')
    return y


num=0
i=1
print('导出中：')
while i<row_num:
    if  full_date [i,0] != full_date[i-1,0] :
        station_num = station_num+1
        out=full_date[num:i,:]
        main(out)
        num=i
    if i%1000==0:
        print(i, '/', row_num)
    i=i+ 1

#调试====================================================================
# # # out=main(full_date[45:51,:])
# # out=main(full_date[690:696,:])
# out = main(full_date[4993:5000, :])
# out=kmeans(full_date[0:9, :])
# # # # out=randctr(full_date[0:9, :])
# # print('==')
# # print(out[:,6:10])
# print(out)

# # # out2= np.insert(out,0,main(full_date[45:51,:]),axis=0)
# print(out)
# # df = pd.DataFrame(out)
# # df.to_csv("test.csv", index=False, sep=',')

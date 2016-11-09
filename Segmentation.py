# -*- coding: cp936 -*-
import codecs
import math
import copy
import os
from collections import Counter

#将结果输出到文件
def writestr(filename,string):
    output=codecs.open(filename,'a',encoding='gbk')
    output.write(string)
    output.close()

#若存在同名文件则删除
def init(filename):
    if os.path.exists(filename):
        os.remove(filename)

#读入字典
def get_dic(filename):
    input=codecs.open(filename,encoding='gbk')
    dic=Counter()
    for line in input:
        tokens=line.strip().split()
        small_dic[tokens[0]]+=1
    input.close()
    for key in small_dic:
        c=key[0] #用每个词中第一个字作索引
        if dic[c]==0:
            dic[c]=Counter()
        if dic[c][len(key)]==0:
            dic[c][len(key)]=[]
        dic[c][len(key)].append(key)
    return dic

#计算切分好的句子的得分
def get_score(words,labels):
    score=0.0
    i=0
    while i<len(words):
        length=0
        if labels[i]=='B':
            while labels[i+length]!='E':
                length+=1
            for j in range(length+1):
                if length==1:
                    lamda=0.99
                elif length==2:
                    lamda=0.9
                elif length==3:
                    lamda=0.85
                else:
                    lamda=0.85
                score+=trans[words[i+j],labels[i+j]]*lamda
                if i>=1:
                    score+=shoot[labels[i+j-1],labels[i+j]]
                else:
                    score+=single[labels[i+j]]
            i+=length
        else:
            score+=trans[words[i],labels[i]]
            if i>=1:
                score+=shoot[labels[i-1],labels[i]]
            else:
                score+=single[labels[i]]
        i+=1
    return score

#初始化用于全切分的有向图的邻接表
def init_graph(sentence):
    length=len(sentence)
    graph=Counter()
    state=Counter()
    for i in range(length):
        graph[i]=[]
        state[i]=[]
        #graph[i].append(i+1)
        state[i].append(0)
    for i in range(length):
        tmp_count=1
        ch=sentence[i]
        sub_dic=dic[ch]
        if sub_dic==0:
            graph[i].append(i+1)
            state[i].append(0)
            continue
        # 'i:',i
        for j in range(i+1,length):
            #print 'j:',j
            ch+=sentence[j]
            tmp_count+=1
            if sub_dic[tmp_count]==0:
                continue
            if ch in sub_dic[tmp_count]:
                graph[i].append(j+1)
                state[i].append(0)
        if not graph[i]:
            graph[i].append(i+1)
            state[i].append(0)
    return (graph,state)

#计算所有切分路径
def get_path(g,s):
    all_path=[]
    single_path=[]
    length=len(g)
    single_path.append(0)
    while not single_path==[]:
		
        top=single_path[-1]
        if single_path[-1]==length:
            ls=copy.deepcopy(single_path)
            all_path.append(ls)
            single_path.pop()
            continue
        
        count=0
        for i in range(len(g[top])):
            if s[top][i]==0: #s用于保存对应位置是否被访问过
                single_path.append(g[top][i])
                s[top][i]=1
                break
            else:
                count+=1
            if count == len(g[top]):
                d=single_path.pop()
                for i in range(len(g[d])):
                    s[d][i]=0 #一个节点访问完栈顶节点出栈时对应访问状态清空
    return all_path

#根据划分的词进行BMES标注
def labeling(word,words,labels):
    length=len(word)
    if length==1:
        words.append(word[0])
        labels.append('S')
    elif length==2:
        words.append(word[0])
        labels.append('B')
        words.append(word[1])
        labels.append('E')
    elif length>2:
        words.append(word[0])
        labels.append('B')
        for i in range(length-2):
            words.append(word[i+1])
            labels.append('M')
        words.append(word[length-1])
        labels.append('E')   

#计算转移概率和发射概率
def compute_pro(filename):
    input=codecs.open(filename,encoding='gbk')
    unigram=Counter()
    bigram=Counter()
    cooc=Counter()
    wordcount=Counter()
    small_dic=Counter()
    for line in input:
        words=[]
        labels=[]
        tokens=line.strip().split()
        for sample in tokens:
            wor=sample.split('/')
            tmp=''
            if wor[1]==u'w':
                continue
            else:
                length=len(wor[0])
                if wor[0][0]==u'[':
                    tmp=wor[0][1:length]
                else:
                    tmp=wor[0]
                labeling(tmp,words,labels)
                small_dic[tmp]+=1
        for i in range(len(words)):
            unigram[labels[i]]+=1
            wordcount[words[i]]+=1
            cooc[words[i],labels[i]]+=1
            if i>1:
                bigram[labels[i-1],labels[i]]+=1
    lamda=1e-5
    shoot=Counter()
    trans=Counter()
    single=Counter()
    total=0
    for key in unigram:
        total+=unigram[key]

    for key in unigram:
        single[key]=unigram[key]*1.0/total

    for key1 in unigram:
        for key2 in unigram:
            probability=(1.0-lamda)*bigram[key1,key2]/unigram[key1]+lamda*single[key1] #用回退进行平滑处理
            shoot[key1,key2]=math.log(probability)

    for word in wordcount:
        for label in unigram:
            probability=(1.0-lamda)*cooc[word,label]/unigram[label]+lamda*single[label]
            trans[word,label]=math.log(probability)
    return (shoot,trans,single,small_dic)

#返回输入词的BMES标注序列
def get_tags(p):
    tags=[]
    for div in p:
        tag=[]
        for i in range(1,len(div)):
            num=div[i]-div[i-1]
            if num==1:
                tag.append('S')
            elif num==2:
                tag.append('B')
                tag.append('E')
            else:
                tag.append('B')
                for i in range(num-2):
                    tag.append('M')
                tag.append('E')
        tags.append(tag)
    return tags

#根据BMES标注返回词序列的输出格式
def get_st(words,tags):
    string=''
    for i in range(len(words)):
        if tags[i]=='S' or tags[i]=='E':
            string+=words[i]+'/ '
        else:
            string+=words[i]
    return string

#预测切分序列
def get_res(filename):
    input=codecs.open(test_file,encoding='gbk')
    for line in input:
        if len(line)<2:
            writestr(res_file,name)
            continue
        seg=''
        limit=len(line)-1
        i=0
        #预处理
        while i<=limit:
            if line[i] not in total_pun:#当前字不在标点集中
                seg+=line[i]
                if i<limit and line[i+1] in total_pun:#若下一个字在标点集中，用空格隔开
                    seg+=' '
            else:#当前字在标点集中
                seg+=line[i]
                if i<limit and line[i+1] in special_pun:#下一个字是时间词，直接读入并加空格隔开
                    seg+=line[i+1]+' '
                    i+=1
                elif i<limit and line[i+1] not in total_pun:#下一个字不在标点集中，用空格隔开
                    seg+=' '
            i+=1
        tokens=seg.strip().split()
        string=''
        #对预处理得到的每段进行处理
        for st in tokens:
            if st[0] in total_pun:#当前词第一个字在标点集中
                i=0
                tags=''
                while i<len(st):
                    if st[i] in single_pun:#如果在真标点集中
                        if i<len(st)-1 and st[i]!=st[i+1]:#如果不是多字节符号则直接作为单字保存到输出序列
                            tags+=st[i]+'/ '
                        else:#如果是多字节符号则先不加分隔号
                            tags+=st[i]
                    elif st[i] in digit:#如果是数字
                        tags+=st[i]
                        if i<len(st)-1 and st[i+1] not in digit+special_pun:#如果后面不是数字或时间词，加分隔号
                            tags+='/ '
                    elif st[i] in letter:#如果是字母，在后面加分隔号
                        tags+=st[i]+'/ '
                        if i<len(st)-1 and st[i+1] not in letter:
                            tags+='/ '
                    else:#如果不属于上述集合则直接保存
                        tags+=st[i]
                    i+=1
                if tags[-1]!=' ':
                    tags+='/ '
                string+=tags
            else:
                if len(st)<2:#如果是单字，在后面加分隔号
                    string+=st+'/ '
                else:#如果不是单字
                    (graph,state)=init_graph(st)#初始化有向图
                    path=get_path(graph,state)#计算全切分路径
                    #print len(path)
                    labels=get_tags(path)#计算BMES标注序列
                    label=[]
                    score=-1100000.0
                    for i in range(len(labels)):
                        tmp=get_score(st,labels[i])#计算每条路径得分
                        if tmp>score:
                            score=tmp
                            label=labels[i]
                    string+=get_st(st,label)#根据得到BMES标注返回输出格式
        string+='\r\n'
        writestr(res_file,string)
    input.close()

if __name__=="__main__":
    training_file='./199801.txt'
    dic_file='./199801dic.txt'
    test_file='./199802_devtxt.txt'
    res_file='./result.txt'

    
    (shoot,trans,single,small_dic)=compute_pro(training_file)
    dic=get_dic(dic_file)

    single_pun=u'，。？！：；‘’“”、－』『《》（）％…×—'
    digit=u'１２３４５６７８９０．'
    letter=u'ＡＢＣＤＥＦＧＨＩＧＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺ'
    special_pun=u'％年月日时分秒万亿'

    total_pun=single_pun+digit+letter

    init(res_file)
    get_res(res_file)
    #st=u'巨蟒似的乌金'
    #(graph,state)=init_graph(st)#初始化有向图
    #print 'init', graph
    #path=get_path(graph,state)#计算全切分路径
    #print len(path)

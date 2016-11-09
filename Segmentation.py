# -*- coding: cp936 -*-
import codecs
import math
import copy
import os
from collections import Counter

#�����������ļ�
def writestr(filename,string):
    output=codecs.open(filename,'a',encoding='gbk')
    output.write(string)
    output.close()

#������ͬ���ļ���ɾ��
def init(filename):
    if os.path.exists(filename):
        os.remove(filename)

#�����ֵ�
def get_dic(filename):
    input=codecs.open(filename,encoding='gbk')
    dic=Counter()
    for line in input:
        tokens=line.strip().split()
        small_dic[tokens[0]]+=1
    input.close()
    for key in small_dic:
        c=key[0] #��ÿ�����е�һ����������
        if dic[c]==0:
            dic[c]=Counter()
        if dic[c][len(key)]==0:
            dic[c][len(key)]=[]
        dic[c][len(key)].append(key)
    return dic

#�����зֺõľ��ӵĵ÷�
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

#��ʼ������ȫ�зֵ�����ͼ���ڽӱ�
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

#���������з�·��
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
            if s[top][i]==0: #s���ڱ����Ӧλ���Ƿ񱻷��ʹ�
                single_path.append(g[top][i])
                s[top][i]=1
                break
            else:
                count+=1
            if count == len(g[top]):
                d=single_path.pop()
                for i in range(len(g[d])):
                    s[d][i]=0 #һ���ڵ������ջ���ڵ��ջʱ��Ӧ����״̬���
    return all_path

#���ݻ��ֵĴʽ���BMES��ע
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

#����ת�Ƹ��ʺͷ������
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
            probability=(1.0-lamda)*bigram[key1,key2]/unigram[key1]+lamda*single[key1] #�û��˽���ƽ������
            shoot[key1,key2]=math.log(probability)

    for word in wordcount:
        for label in unigram:
            probability=(1.0-lamda)*cooc[word,label]/unigram[label]+lamda*single[label]
            trans[word,label]=math.log(probability)
    return (shoot,trans,single,small_dic)

#��������ʵ�BMES��ע����
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

#����BMES��ע���ش����е������ʽ
def get_st(words,tags):
    string=''
    for i in range(len(words)):
        if tags[i]=='S' or tags[i]=='E':
            string+=words[i]+'/ '
        else:
            string+=words[i]
    return string

#Ԥ���з�����
def get_res(filename):
    input=codecs.open(test_file,encoding='gbk')
    for line in input:
        if len(line)<2:
            writestr(res_file,name)
            continue
        seg=''
        limit=len(line)-1
        i=0
        #Ԥ����
        while i<=limit:
            if line[i] not in total_pun:#��ǰ�ֲ��ڱ�㼯��
                seg+=line[i]
                if i<limit and line[i+1] in total_pun:#����һ�����ڱ�㼯�У��ÿո����
                    seg+=' '
            else:#��ǰ���ڱ�㼯��
                seg+=line[i]
                if i<limit and line[i+1] in special_pun:#��һ������ʱ��ʣ�ֱ�Ӷ��벢�ӿո����
                    seg+=line[i+1]+' '
                    i+=1
                elif i<limit and line[i+1] not in total_pun:#��һ���ֲ��ڱ�㼯�У��ÿո����
                    seg+=' '
            i+=1
        tokens=seg.strip().split()
        string=''
        #��Ԥ����õ���ÿ�ν��д���
        for st in tokens:
            if st[0] in total_pun:#��ǰ�ʵ�һ�����ڱ�㼯��
                i=0
                tags=''
                while i<len(st):
                    if st[i] in single_pun:#��������㼯��
                        if i<len(st)-1 and st[i]!=st[i+1]:#������Ƕ��ֽڷ�����ֱ����Ϊ���ֱ��浽�������
                            tags+=st[i]+'/ '
                        else:#����Ƕ��ֽڷ������Ȳ��ӷָ���
                            tags+=st[i]
                    elif st[i] in digit:#���������
                        tags+=st[i]
                        if i<len(st)-1 and st[i+1] not in digit+special_pun:#������治�����ֻ�ʱ��ʣ��ӷָ���
                            tags+='/ '
                    elif st[i] in letter:#�������ĸ���ں���ӷָ���
                        tags+=st[i]+'/ '
                        if i<len(st)-1 and st[i+1] not in letter:
                            tags+='/ '
                    else:#�������������������ֱ�ӱ���
                        tags+=st[i]
                    i+=1
                if tags[-1]!=' ':
                    tags+='/ '
                string+=tags
            else:
                if len(st)<2:#����ǵ��֣��ں���ӷָ���
                    string+=st+'/ '
                else:#������ǵ���
                    (graph,state)=init_graph(st)#��ʼ������ͼ
                    path=get_path(graph,state)#����ȫ�з�·��
                    #print len(path)
                    labels=get_tags(path)#����BMES��ע����
                    label=[]
                    score=-1100000.0
                    for i in range(len(labels)):
                        tmp=get_score(st,labels[i])#����ÿ��·���÷�
                        if tmp>score:
                            score=tmp
                            label=labels[i]
                    string+=get_st(st,label)#���ݵõ�BMES��ע���������ʽ
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

    single_pun=u'��������������������������������������������'
    digit=u'����������������������'
    letter=u'���£ãģţƣǣȣɣǣˣ̣ͣΣϣУѣңӣԣգ֣ףأ٣�'
    special_pun=u'��������ʱ��������'

    total_pun=single_pun+digit+letter

    init(res_file)
    get_res(res_file)
    #st=u'�����Ƶ��ڽ�'
    #(graph,state)=init_graph(st)#��ʼ������ͼ
    #print 'init', graph
    #path=get_path(graph,state)#����ȫ�з�·��
    #print len(path)

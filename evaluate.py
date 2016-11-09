import codecs

pred=codecs.open('result.txt',encoding='gbk')
correct=codecs.open('199802_dev.txt',encoding='gbk')

def getset(fileio):
        set=[]
        total=0
        for line in fileio:
                cnt=0
                if line=='\r\n':
                        continue
                tokens=line.strip().split()
                total+=len(tokens)
                tmp={}
                for word in tokens:
                        if word[0]==u'[' and len(word)>1:
                                word=word.strip(u'[')
                        wor=word.split(u'/')
                        tmp[cnt]=wor[0]
                        cnt+=len(wor[0])
                set.append(tmp)
        return (set,total)
                
if __name__=="__main__":
        (pre_set,pre_total)=getset(pred)
        (cor_set,cor_total)=getset(correct)
        print "number of sentences:",len(pre_set)
        correct_cnt=0
        for sent_i in range(len(pre_set)):
                for word_i in pre_set[sent_i]:
                        if word_i in cor_set[sent_i] and cor_set[sent_i][word_i]==pre_set[sent_i][word_i]:
                                correct_cnt+=1
        p = float(correct_cnt)/pre_total
        r = float(correct_cnt)/cor_total
        print 'precise:{:.2f}%'.format(p*100)
        print 'recall:{:.2f}%'.format(r*100)
        print 'F1 score:{:.2f}%'.format(200*p*r/(p+r))


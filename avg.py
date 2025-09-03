
def calc_avg_response():

    with open("app/prediction.txt", "r") as s:
        pred = s.readlines()
        cl_pred=list(map(str.strip,pred))
    count_neg=0
    count_pos=0
    for i in cl_pred:
        if i=='POSITIVE':
            count_pos+=1
        else:
            count_neg+=1

    #print("pos: ",count_pos)
    #print("neg: ",count_neg)

    total=len(cl_pred)

    #print("total predictions: ",total)

    avg_pos=count_pos/total
    #print(avg_pos)

    avg_neg=count_neg/total
    #print(avg_neg)

    if avg_pos>avg_neg:
        response="Most responses are POSITIVE"
    elif avg_pos==avg_neg:
        response="Responses are both equally positive and negative"
    else:
        response="Most responses are NEGATIVE"

    return response


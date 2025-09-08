
def calc_avg_response():

    with open("/app/prediction.txt", "r") as s:
    # with open("prediction.txt", "r") as s:
        pred = s.readlines()
        cl_pred=list(map(lambda x: int(x.strip()),pred))

    total=len(cl_pred)

    summ=sum(cl_pred)

    avg_pos=summ/total
    return avg_pos






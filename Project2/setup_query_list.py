__author__ = 'johnfulgoni'


def setup_query_list(FILENAME):
    file = open(FILENAME+'.txt', 'r')
    query_list = []
    #category_list = []

    if FILENAME == 'root':
        category_list = ['Computers', 'Health', 'Sports']
        query_list.append([])
        query_list.append([])
        query_list.append([])
    if FILENAME == 'computers':
        category_list = ['Hardware', 'Programming']
        query_list.append([])
        query_list.append([])
    if FILENAME == 'health':
        category_list = ['Diseases', 'Fitness']
        query_list.append([])
        query_list.append([])
    if FILENAME == 'sports':
        category_list = ['Soccer', 'Basketball']
        #category_list.append('Soccer')
        #category_list.append('Basketball')
        query_list.append([])
        query_list.append([])

    print category_list
    for line in file:
        sp = line.strip().split(' ')
        category = sp.pop(0)
        #print category
        list_index = category_list.index(category)

        query_list[list_index].append(sp)
        # if len(sp) < 2:
        #     query_list[list_index].append((sp[0], None))
        # else:
        #     query_list[list_index].append(tuple(sp))

    file.close()

    return query_list


def main():
    file_list = {'root', 'computers', 'health', 'sports'}
    all_query_lists = []

    for file in file_list:
        all_query_lists.append(setup_query_list(file))
    #all_query_lists.append(setup_query_list('sports'))
    print all_query_lists
    # first dimension is the file, so root, computers, health or sports
    # second dimension is the category, so computers, health, sports
    print all_query_lists[0][2][0]

if __name__=="__main__":
    main()
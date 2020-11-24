setTable = ['Global', 'Global/CN/Pod2/我自己起飞/515火箭发射中心', 'Global/CN/Pod3', 'Global/CN/Pod3/HQU',
            'Global/CN/Pod3/HQU/Floor1', 'Global/CN/Pod2', 'Global/CN', 'Global/CN/Pod2/我自己起飞',
            'Global/CN/SH', 'Global/CN/SH/Pod9', 'Global/CN/Pod6', 'Global/CN/Pod6/DNA grady',
            'Global/CN/Pod6/DNA grady/west', 'Global/CN/DNA Center Guide Building', 'Global/DE',
            'Global/DE/Pod7', 'Global/DE/Pod7/HBF']
# list转dict

USER_DICT = {}
for i in range(len(setTable)):
    USER_DICT[i] = setTable[i]

print(USER_DICT)
old_list = [[0,5,'f'], [4,2,'t'],[9,4,'afsd']]

#let's assume we want to sort lists by last value ( old_list[2] )
new_list = sorted(old_list, key=lambda x: x[1])

#Resulst of new_list will be:

print(new_list)
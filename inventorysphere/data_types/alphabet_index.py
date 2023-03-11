def get_alphabet_index_from_integer(num):
    convertString = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    base = 26
    i = num

    if i < base:
        return convertString[i]
    else:
        return get_alphabet_index_from_integer(i//base - 1) + convertString[i%base]
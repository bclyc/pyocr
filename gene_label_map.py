

if __name__=="__main__":
    f = open("./char_label_map.pbtxt", "w")

    lines = []
    # lines += ["item {\n",
    #     "  id: 0\n",
    #     "  name: 'none_of_the_above'\n",
    #     "}\n",
    #     "\n"]
    char20test = [1510, 2047, 104, 1001, 436, 2228, 1175, 1502, 1011, 1007, 3262, 2502, 2371, 3570, 2113, 2110, 2137,
                  2133, 179, 2868]

    for i in range(0, 20):
        lines += ["item {\n",
                  "  id: "+str(i)+"\n",
                  "  name: '"+str(char20test[i]).zfill(4)+"'\n",
                  "}\n",
                  "\n"]

    f.writelines(lines)
    f.close()
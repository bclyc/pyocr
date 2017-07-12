

if __name__=="__main__":
    f = open("./char_label_map", "w")

    lines = []
    # lines += ["item {\n",
    #     "  id: 0\n",
    #     "  name: 'none_of_the_above'\n",
    #     "}\n",
    #     "\n"]
    for i in range(0, 3590):
        lines += ["item {\n",
                  "  id: "+str(i)+"\n",
                  "  name: '"+str(i).zfill(4)+"'\n",
                  "}\n",
                  "\n"]

    f.writelines(lines)
    f.close()
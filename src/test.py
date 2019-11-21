text = "YOU'RE, NEXT, U, UR, HOLD, DONE, UH UH, WHAT?, UH HUH, YOU, LIKE, SURE, YOU ARE, YOUR"
words = text.split(", ")
for i, word in enumerate(words):
    suffix = ", "
    if i == len(words) - 1:
        suffix = ""
    print("\""+word.lower() + "\"" + suffix, end="")
    if (i+1) % 5 == 0:
        print("")

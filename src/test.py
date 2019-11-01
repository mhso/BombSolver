from enum import Enum

Test = Enum("Colors", {"Black":0, "Yellow":1, "Blue":2, "White":3, "Red":4})
print(Test.Black.value)

from src.entity.Space import Space
from src.form.Line import Line

# [[500,100],[500,400]] @ [451,456]
# [[500,400],[100,400]] @ [451,456]
# [[500,100],[500,400]] @ [450,456]
# [[500,400],[100,400]] @ [450,456]
print(Line(Space(1,0), Space(1,1)).cross_line(Line(Space(2,1), Space(0,1))))
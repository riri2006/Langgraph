from pydantic import BaseModel, StrictInt, StrictStr, Field
from typing import Optional

#Int me "" string dala still it typcasted that as int
class Student(BaseModel):
    name: str
    age: int
student = Student(name="Riddhi", age="20")
print(student)

##strictInt 
class Fruit(BaseModel):
    name: str
    units: StrictInt
fruit1 = Fruit(name="Mango", units=100)
print(fruit1)
try:
    fruit2 = Fruit(name="Lychee", units="100")
    print(fruit2)
except :
    print("Invalid data type")

#optional
class Employee(BaseModel):
    name: str
    age: int
    salary: Optional[float] = None

emp1 = Employee(name="Riddhi", age=20, salary=95000)
emp2 = Employee(name="Kashish", age=25)
print(emp1)
print(emp2)

#LIST INPUT - if u write tuple that will also bhi typecasted as list

class Classroom(BaseModel):
    floor: int
    children: list[StrictStr]

cls1 = Classroom(floor=1,children=["Riddhi","Vedant","Kashish"])
print(cls1)
cls2 =Classroom(floor=2, children=["Riddhi", "123"])
print(cls2)

#access state in other state variable
class Colour(BaseModel):
    colour1 : str
    colour2 : str

class Flower(BaseModel):
    name: str
    colors : Colour

flower = Flower(
    name= "Lily",
    colors={"colour1":"White", "colour2":"Pink"} 
    #when we give multiple values for a single argument , then we use dictionary
)
print(flower)


#Field - used for giving extra description and extra rules regulations
#DEFAULT- SETTING DEFAULT VALUE TO ANY PARAMETER
class Movie(BaseModel):
    name: str 
    year : int = Field(gt=1800, le= 2026 )
    ratings: float =Field(default=3.0, lt=5.0, gt=0.9)

try:
    movie1 = Movie(name= "Krishnavtaram", year=2026, ratings=4.8)
    print(movie1)
    movie2 = Movie(name="IT: Welcome to Derry", year=2025)
    print(movie2)
    movie3 = Movie(name="Harry Potter", year=1800)
    print(movie3)

except:
    print("INVALID YEAR OR MOVIE.")


#to see schema
print(Flower.schema())


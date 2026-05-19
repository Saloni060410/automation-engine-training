import json
import requests

#get request 
r=requests.get("https://jsonplaceholder.typicode.com/posts")

#parses data to json
data=r.json()

key = data[0].keys()
print(key)
#dict_keys(['userId', 'id', 'title', 'body'])

uid={item["userId"] for item in data}
print("unique userid :", list(uid))

i={item["id"] for item in data}
print("unique id :", list(i))

# unique userid : [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
# unique id : [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100]

targeted_users=4
#filtering on the basis of userid... for userid=4
filtering=[p for p in data if p['userId']==targeted_users]

#printing properly 
print("data for userId :",targeted_users,"\n")

for x in filtering:
    print(f"Post ID : {x['id']}")
    print(f"Title : {x['title']}")
    print(f"Body  : {x['body']}\n\n")





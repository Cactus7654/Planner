tasks = [
    {"id": 1, "title": "Купить продукты", "status": "новая", "priority": 2},
    {"id": 2, "title": "Сделать домашку", "status": "в работе", "priority": 3},
    {"id": 3, "title": "Позвонить маме", "status": "готова", "priority": 1},
]
# v - это описание задачи, а z - приоритетность
def add_task(v, z):
    maxima_id = tasks[-1].get("id")
    tasks.append({"id": maxima_id + 1, "title": v, "status": "готова", "priority": z})
    return 1

add_task("Вынести мусор", 2)
add_task("принести мусор", 3)
add_task("сжечь мусор", 1)

for elem in tasks:
    print(elem)



class MySingleton(Singleton):
    def __init__(self):
        self.value = None

obj1 = MySingleton()
obj2 = MySingleton()

obj1.value = 'Singleton Pattern'
print(obj2.value)  # Output: Singleton Pattern
print(obj1 is obj2)  # Output: True
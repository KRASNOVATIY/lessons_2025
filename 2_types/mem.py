# помните мем из лекции? Посмотрим на что способен Питон...
# Умножение экземпляра класса на строку
class ClassOnStrMultiplier:
    base = 10

    def __mul__(self, other):  # <- этот магический метод определяет операцию умножения
        return self.base * other


instance = ClassOnStrMultiplier()
result = instance * 'str'  # <- вот само умножение
print(result)


# Как можно умножить сам класс на строку???
class MetaClassOnStrMultiplier(type):  # <- мы определяем метакласс, то есть класс создающий классы, а не экземпляры класса
    base = 10

    def __mul__(cls, other):  # <- так как у нас метакласс, его экзепляры не self, а cls (это соглашение)
        return cls.base * other


class NewClassOnStrMultiplier(metaclass=MetaClassOnStrMultiplier):  # <- создаём класс с использованием метакласса
    ...


result = NewClassOnStrMultiplier * 'str'  # <- вот само умножение
print(result)

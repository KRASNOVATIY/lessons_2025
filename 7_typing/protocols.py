from dataclasses import dataclass
from typing import Protocol, runtime_checkable


@runtime_checkable  # это добавит проверку соответствия во время выполнения программы
class EngineProtocol(Protocol):
    def run(self):
        ...


@dataclass
class PetrolEngine(EngineProtocol):
    def run(self):
        print('ж-ж-ж')

    def stall(self):
        print('заглох')


@dataclass
class JetEngine(EngineProtocol):
    def run(self):
        print('у-у-у')

    def fly(self):
        print('летим')


@dataclass
class HorseEngine:  # Явно не указали протокол
    def run(self):
        print('дык-дык')

    def eat(self):
        print('мням')


@dataclass
class Hum:  # Явно не указали протокол
    def step(self):
        print('цок')


@dataclass
class Car:
    e: EngineProtocol  # обратите внимание! Явно указали тип

    def poehali(self):
        self.e.run()


def main():
    p = PetrolEngine()
    j = JetEngine()
    h = HorseEngine()
    cp = Car(p)
    cp.poehali()
    cj = Car(j)
    cj.poehali()
    ch = Car(h)
    ch.poehali()

    hum_e = Hum()
    c = Car(hum_e)
    c.poehali()


if __name__ == '__main__':
    main()
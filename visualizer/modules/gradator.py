class Gradator:

    def __init__(self, min_value: tuple, max_value: tuple) -> None:
        self.__min_value = min_value
        self.__max_value = max_value

    def get_colors(self, step: int) -> list:
        colors = list()
        for i in range(step):
            colors.append(self.__get_color(i / step))
        return colors

    def __get_color(self, value: float) -> tuple:
        r = self.__get_value(self.__min_value[0], self.__max_value[0], value)
        g = self.__get_value(self.__min_value[1], self.__max_value[1], value)
        b = self.__get_value(self.__min_value[2], self.__max_value[2], value)
        return (r, g, b)

    def __get_value(self, min_value: int, max_value: int, value: float) -> int:
        return int(min_value + (max_value - min_value) * value)

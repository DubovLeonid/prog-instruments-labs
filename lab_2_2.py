import math
from scipy.special import erfc, gammainc
from saveopenload import load_json, read


def frequency_test(bits:str)->float:
    """
    Частотный побитовый тест (Frequency Test).
    Проверяет, насколько количество 1 и 0 близко к равному.
    :param bits: строка из '0' и '1'
    :return: p-value
    """

    n = len(bits)
    s = sum(1 if bit == '1' else -1 for bit in bits) / math.sqrt(n)
    p_value = math.erfc(abs(s) / math.sqrt(2))
    return p_value


def runs_test(bits:str)->float:
    """
    Выполняет тест на одинаковые подряд идущие биты
    :param bits: Бинарная строка для тестирования
    :return: P-значение теста
    """
    n = len(bits)
    pi = bits.count('1') / n

    if abs(pi - 0.5) >= (2 / math.sqrt(n)):
        return 0.0

    vn = sum(1 for i in range(n - 1) if bits[i] != bits[i + 1])
    numerator = abs(vn - 2 * n * pi * (1 - pi))
    denominator = 2 * math.sqrt(2 * n) * pi * (1 - pi)
    return erfc(numerator / denominator)


from scipy.special import gammaincc


def longest_run_test(bits: str) -> float:
    """
    Тест на самую длинную последовательность единиц в блоке.
    Анализирует распределение максимальных длин последовательностей единиц.
    :param bits: Битовая строка длиной не менее 128 символов (кратно 8).
    :return: P-значение теста. Значение >= 0.01 указывает на успешное прохождение теста.
    """

    if len(bits) < 128:
        raise ValueError("Minimum 128 bits required")
    config = load_json("nastrli.json")
    pi = config['pi_values']
    num_blocks = len(bits) // 8
    val = [0, 0, 0, 0]

    for i in range(num_blocks):
        block = bits[i * 8:(i + 1) * 8]
        max_run = 0
        current_run = 0
        for bit in block:
            current_run = current_run + 1 if bit == '1' else 0
            max_run = max(max_run, current_run)

        match max_run:
            case 0 | 1:
                val[0] += 1
            case 2:
                val[1] += 1
            case 3:
                val[2] += 1
            case _:
                val[3] += 1

    chi_sq = sum((v - 16 * p) ** 2 / (16 * p) for v, p in zip(val, pi))
    p_value = gammaincc(1.5, chi_sq / 2)
    return p_value


def read_bits(filename:str)->str | None:
    """
        Считывает последовательность битов из файла и проверяет её валидность.
        Проверяет:
        1. Ровно 128 бит в последовательности
        2. Только символы '0' и '1' в содержимом
        :param filename: Название файла с последовательностью битов
        :return: Валидная битовая строка или None при ошибке
        """
    try:
        bits=read(filename)
        if len(bits) != 128:
            raise ValueError(f"Файл {filename} содержит {len(bits)} бит вместо 128")
        if not set(bits) <= {'0', '1'}:
            raise ValueError(f"Файл {filename} содержит недопустимые символы")
        return bits
    except ValueError as ve:
        print(f"Ошибка данных: {ve}")
        return None


def test_sequence(bits: str, name: str) -> None:
    """
        Выполняет серию статистических тестов NIST для анализа случайности битовой последовательности.
        :param bits (str): Битовая последовательность для тестирования (должна содержать только '0' и '1')
        :param name (str): Название/идентификатор последовательности для вывода в отчет
    """
    try:
        print(f"\n{'=' * 40}")
        print(f"Тестирование последовательности: {name}\n")

        # Список тестов и их результатов (название, p-value, пройден ли)
        tests = [
            ("Частотный тест", frequency_test(bits)),
            ("Тест на серии", runs_test(bits)),
            ("Тест на длинные последовательности", longest_run_test(bits))
        ]

        # Проверка и вывод результатов для каждого теста
        passed_all = True
        for idx, (test_name, p_value) in enumerate(tests, 1):
            passed = p_value >= 0.01 if p_value is not None else False
            passed_all &= passed

            status = "ПРОЙДЕН" if passed else "НЕ ПРОЙДЕН"
            print(f"[{idx}] {test_name}:")
            print(f"  p-value = {p_value:.6f}")
            print(f"  Статус: {status}\n")

        # Итоговый результат
        print("\nИтоговые результаты:")
        result_status = "Все тесты пройдены успешно " if passed_all else "Есть непройденные тесты "
        print(result_status)

    except Exception as e:
        print(f"\nОшибка при тестировании: {str(e)}")


def main():
    config=load_json("nastrli.json")
    files = [(item["filename"], item["name"]) for item in config["files"]]
    for filename, name in files:
        bits = read_bits(filename)
        if bits:
            test_sequence(bits, name)


if __name__ == "__main__":
    main()
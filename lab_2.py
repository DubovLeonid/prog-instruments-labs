import math
from scipy.special import erfc, gammainc
def frequency_test(bits):
    """
        Частотный побитовый тест
        Проверяет, является ли количество единиц и нулей в последовательности примерно одинаковым.
        :param bits: Битовая строка для анализа
        :return: P-значение теста
        """

    n = len(bits)
    s = sum(1 if bit == '1' else -1 for bit in bits) / math.sqrt(n)
    p_value = math.erfc(abs(s) / math.sqrt(2))
    return p_value

def runs_test(bits):
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


def longest_run_test(bits):
    """
        Тест на самую длинную последовательность единиц в блоке
        Анализирует распределение максимальных длин последовательностей единиц.
        :param bits: Битовая строка для анализа
        :return: P-значение теста
        """

    blocks = [bits[i*8:(i+1)*8] for i in range(16)]
    v = [0, 0, 0, 0]
    pi = [0.2148, 0.3672, 0.2305, 0.1875]

    for block in blocks:
        max_run = 0
        current_run = 0
        for bit in block:
            current_run = current_run + 1 if bit == '1' else 0
            max_run = max(max_run, current_run)
        if max_run <= 1: v[0] += 1
        elif max_run == 2: v[1] += 1
        elif max_run == 3: v[2] += 1
        else: v[3] += 1

    chi_sq = sum((v[i] - 16 * pi[i])**2 / (16 * pi[i]) for i in range(4))
    return gammainc(1.5, chi_sq / 2)


def read_bits(filename):
    """
    Считывает последовательность и проверяет на количество бит
    :param filename: название файла с последовательностью
    :return:
    """
    try:
        with open(filename, 'r') as f:
            bits = f.read().strip()
            if len(bits) != 128:
                raise ValueError(f"Файл {filename} содержит {len(bits)} бит вместо 128")
            if not set(bits) <= {'0', '1'}:
                raise ValueError(f"Файл {filename} содержит недопустимые символы")
            return bits
    except FileNotFoundError:
        print(f"Ошибка: файл {filename} не найден!")
        return None
    except Exception as e:
        print(f"Ошибка при чтении {filename}: {str(e)}")
        return None


def test_sequence(bits, name):
    """
        Выполняет серию статистических тестов NIST для анализа случайности битовой последовательности.
        :param bits (str): Битовая последовательность для тестирования (должна содержать только '0' и '1')
        :param name (str): Название/идентификатор последовательности для вывода в отчет
    """

    try:
        print(f"\n{'=' * 40}")
        print(f"Тестирование последовательности: {name}")

        p1 = frequency_test(bits)
        print(f"\n[1] Частотный тест: p-value = {p1:.6f}")

        p2 = runs_test(bits)
        print(f"[2] Тест на серии: p-value = {p2:.6f}")

        p3 = longest_run_test(bits)
        print(f"[3] Тест на длинные последовательности: p-value = {p3:.6f}")

        print("\nИтоговые результаты:")
        print(f"Все тесты пройдены: {all(p >= 0.01 for p in [p1, p2, p3])}")

    except Exception as e:
        print(f"\nОшибка при тестировании: {str(e)}")


def main():
    files = [
        ("cpp_random_bits.txt", "C++ ГПСЧ"),
        ("java_random_bits.txt", "Java SecureRandom")
    ]

    for filename, name in files:
        bits = read_bits(filename)
        if bits:
            test_sequence(bits, name)


if __name__ == "__main__":
    main()
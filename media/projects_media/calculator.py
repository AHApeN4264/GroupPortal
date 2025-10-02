#expression - вираз (математичний); digit - цифра; numbers - числа; operators - знаки (математичні)
def calculator(expression):
    #Перевіряємо вираз на ті помилки, що можемо перевірити зараз
    if type(expression) != str: raise ValueError("Вираз має бути поданий як str")
    elif len(expression) == 0: raise ValueError("Вираз не може бути пустим")
    for char in expression:
        if char not in " 0123456789.+-*/^()":
            raise ValueError(f"Вираз не може містити такий символ: {char}")

    #Видаляємо усі пробіли з виразу
    expression = expression.replace(" ", "")
    
    #Створюємо змінні для зберігання цифер та математичних знаків
    digits = "0123456789."
    operators = "+-*/^"
    
    #Перетворюємо текстовий вираз в список з чисел, знаків між ними та виразів в дужках
    e = []
    brackets = 0
    for char in expression:
        if brackets > 0: #Якщо дужки вже відкриті
            if char == "(":
                brackets += 1
            elif char == ")":
                brackets -= 1
            e[-1] += char
        elif char in operators: #Якщо це якийсь математичний знак
            e.append(char)
        elif char in digits: #Якщо це якась цифра
            if len(e) == 0:
                e.append(char)
            elif e[-1][-1] in digits:
                e[-1] += char
            elif (len(e) == 1 and e[0] == "-") or (len(e) > 1 and e[-1] == "-" and e[-2] in operators):
                e[-1] += char
            else:
                e.append(char)
        elif char == "(": #Якщо дужка відкривається
            e.append("(")
            brackets += 1
        else: #Сюди можна потрапити лише якщо дужка закривається не відкрившись
            raise ValueError("В виразі є дужка, що закривається не відкрившись")
    if brackets > 0: raise ValueError("В виразі є дужка, що відкравається не закрившись")

    #Замінюю всі вирази в дужках, на їх результати
    expression = []
    for i in e:
        if i[0] == "(": expression.append(calculator(i[1:-1]))
        else: expression.append(i)

    #Скорочую вираз поки не залишеться число-відповідь, виконуючи дії в правильному порядку
    while "^" in expression: #Виконую усі підняття до степенню
        i = expression.index("^")
        if i > 0 and i < len(expression)-1 and expression[i-1] not in operators and expression[i+1] not in operators:
            expression[i] = str(float(expression[i-1]) ** float(expression[i+1]))
            expression.pop(i-1)
            expression.pop(i)
        else: raise ValueError("В виразі є помилка при використанні знаку піднесення до степеню")
    while "*" in expression or "/" in expression: #Виконую усі множення та ділення
        if "*" in expression and "/" in expression:
            i_m, i_d = expression.index("*"), expression.index("/")
            if i_m < i_d:
                if i_m > 0 and i_m < len(expression) and expression[i_m-1] not in operators and expression[i_m+1] not in operators:
                    expression[i_m] = str(float(expression[i_m-1]) * float(expression[i_m+1]))
                    expression.pop(i_m-1)
                    expression.pop(i_m)
                else: raise ValueError("В виразі є помилка при використанні знаку множення")
            else:
                if i_d > 0 and i_d < len(expression) and expression[i_d-1] not in operators and expression[i_d+1] not in operators:
                    expression[i_d] = str(float(expression[i_d-1]) / float(expression[i_d+1]))
                    expression.pop(i_d-1)
                    expression.pop(i_d)
                else: raise ValueError("В виразі є помилка при використанні знаку ділення")
        elif "*" in expression:
            i = expression.index("*")
            if i > 0 and i < len(expression) and expression[i-1] not in operators and expression[i+1] not in operators:
                expression[i] = str(float(expression[i-1]) * float(expression[i+1]))
                expression.pop(i-1)
                expression.pop(i)
            else: raise ValueError("В виразі є помилка при використанні знаку множення")
        else:
            i = expression.index("/")
            if i > 0 and i < len(expression) and expression[i-1] not in operators and expression[i+1] not in operators:
                expression[i] = str(float(expression[i-1]) / float(expression[i+1]))
                expression.pop(i-1)
                expression.pop(i)
            else: raise ValueError("В виразі є помилка при використанні знаку ділення")
    while "+" in expression or "-" in expression: #Виконую усі додавання та віднімання
        if "+" in expression and "-" in expression:
            i_p, i_m = expression.index("+"), expression.index("-")
            if i_p < i_m:
                if i_p > 0 and i_p < len(expression) and expression[i_p-1] not in operators and expression[i_p+1] not in operators:
                    expression[i_p] = str(float(expression[i_p-1]) + float(expression[i_p+1]))
                    expression.pop(i_p-1)
                    expression.pop(i_p)
                else: raise ValueError("В виразі є помилка при використанні знаку додавання")
            else:
                if i_m > 0 and i_m < len(expression) and expression[i_m-1] not in operators and expression[i_m+1] not in operators:
                    expression[i_m] = str(float(expression[i_m-1]) - float(expression[i_m+1]))
                    expression.pop(i_m-1)
                    expression.pop(i_m)
                else: raise ValueError("В виразі є помилка при використанні знаку віднімання")
        elif "+" in expression:
            i = expression.index("+")
            if i > 0 and i < len(expression) and expression[i-1] not in operators and expression[i+1] not in operators:
                expression[i] = str(float(expression[i-1]) + float(expression[i+1]))
                expression.pop(i-1)
                expression.pop(i)
            else: raise ValueError("В виразі є помилка при використанні знаку додавання")
        else:
            i = expression.index("-")
            if i > 0 and i < len(expression) and expression[i-1] not in operators and expression[i+1] not in operators:
                expression[i] = str(float(expression[i-1]) - float(expression[i+1]))
                expression.pop(i-1)
                expression.pop(i)
            else: raise ValueError("В виразі є помилка при використанні знаку віднімання")
    
    return expression[0]


print("Дії підтримуванні калькулятором: +, -, *, /, ^, ()")
while True:
    expression = input("Введіть математичний вираз: ")
    print(calculator(expression), end="\n\n")

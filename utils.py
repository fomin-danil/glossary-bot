from fuzzywuzzy import fuzz
from fuzzywuzzy import process
from pymorphy2 import MorphAnalyzer

def lemmatizer(user_input):
    # stop_words = ['как', 'называться', 'что', 'кто', 'такой', 'такой',
                  # 'такие', 'хочу', 'узнать', 'подскажите']
    error_gram = ['LATN', 'PNCT', 'NUMB', 'ROMN', 'UNKN']
    m = MorphAnalyzer()

    """
    Пример. Получили: «Кто такие project-менеджеры?»
    1. Делим инпут на слова.
    2. Убираем прилипшие знаки препинания.
    3. Слова приводим к строчным буквам.
    4. (Если слово не в стоп-листе, анализируем его.)
    5. Берем начальную форму.
    6. Берем часть речи.
    7. Проверяем, какой тег получило слово. Если тег нестандрат-
    ный (error_gram), слово не записываем (это число или знак).
    8. Если тег LATN или UNKN, то слово было написано латиницей 
    или с опечаткой, его берем. Так не упустим "project-manager".
    UNKN беру на всякий случай, потому что pymorphy неплохо
    приписывает части речи и незнакомым словам, т.е. в том числе
    словам с опечатками.
    9. Новая строчка комментария.
    """
    
    # Делим все сообщение пользователя на слова.
    words_from_input = user_input.split()
    user_input_lem = []  # сюда собираем слова в нач. форме
    for word in words_from_input:
        # очистим от знаков препинания, прилипшим к словам
        word = word.strip(')(@#$%,;:.«» ?!\\"\\"')
        word = word.lower()
        word_ana = m.parse(word)[0]  # анализируем форму
        lex = str(word_ana.normal_form) # берем нач. форму
        pos = str(word_ana.tag).split(',')[0] # берем часть речи
        if pos not in error_gram:
            user_input_lem.append(lex + '_' + pos) # записали с тегом
        elif pos == 'LATN' or 'UNKN':
            user_input_lem.append(lex)
        else:
            continue
            
    return user_input_lem

def colloc(user_input_lem):
    # print(user_input_lem)
    noun_p = ['NOUN', 'ADJF','ADJS', 'PREP', 'UNKN']
    nouns_list = []
    bigramms_list = []
    for word in user_input_lem:
        lem = word.split('_')[0]
        try:
            pos = word.split('_')[1]
            # print(word, pos)
        except IndexError:
            pos = ''
            nouns_list.append(lem)
            # break
        # print(lem, pos)
        # print(lem, pos)
        if pos == 'NOUN' or 'VERB' or 'INFN':
            nouns_list.append(lem)
        if pos == 'NOUN' or pos == 'ADJF' or pos == 'ADJS' \
        or pos == 'VERB' or 'INFN' or pos == 'UKNK' \
        and pos != 'PREP':
            position = user_input_lem.index(word)
            position_next = position + 1
            position_next2 = position + 2
            # print(position, position_next)
            if position + 1 < len(user_input_lem):
                lem_next = user_input_lem[position_next].split('_')[0]
                try:
                    pos_next = user_input_lem[position_next].split('_')[1]
                except IndexError:
                    pos_next = 'UNKN'
                search_inq = lem + ' ' + lem_next
                if pos_next in noun_p:
                    bigramms_list.append(search_inq)
            if position + 2 < len(user_input_lem):
                lem_next = user_input_lem[position_next].split('_')[0]
                try:
                    pos_next = user_input_lem[position_next].split('_')[1]
                except IndexError:
                    pos_next = 'UNKN'
                lem_next2 = user_input_lem[position_next2].split('_')[0]
                try:
                    pos_next2 = user_input_lem[position_next2].split('_')[1]
                except IndexError:
                    pos_next2 = 'UNKN'
                search_inq = lem + ' ' + lem_next + ' ' + lem_next2
                if pos_next and pos_next2 in noun_p:
                    bigramms_list.append(search_inq)
                    # print(bigramms_list)
                    
    return nouns_list, bigramms_list

def parse_glossary(filename):
    glossary = {}
    output_terms = {}
    with open(filename, 'r', encoding="utf-8") as f:
        rows = f.readlines()
        m = MorphAnalyzer()
        for row in rows[2:]:
            termins_lem = []
            termin = row.split('\t')[0].strip().split()
            termin_official = str(row.split('\t')[0].strip().capitalize())
            for word in termin:
                word = m.parse(word)[0]
                word = str(word.normal_form)
                termins_lem.append(word)
            glossary[' '.join(termins_lem)] = row.split('\t')[1:]
            output_terms[' '.join(termins_lem)] = termin_official
        f.close()
    return glossary, output_terms

def parse_glossary_trash(filename, output_terms):
    glossary_t = {}
    with open(filename, 'r', encoding="utf-8") as f2:
        rows = f2.readlines()
        m = MorphAnalyzer()
        for row in rows[2:]:
            # print(row.split('\t')[2:])
            term_trash = row.split('\t')[1].split(',')
            # print(term_trash)
            for entry in term_trash:
                termins_lem = []
                termin_official = entry.strip()
                termin = entry.lower().strip().split()
                for word in termin:
                    word = m.parse(word)[0]
                    word = str(word.normal_form)
                    termins_lem.append(word)
                glossary_t[' '.join(termins_lem)] = \
                row.split('\t')[2], row.split('\t')[3]
                output_terms[' '.join(termins_lem)] = \
                row.split('\t')[0].capitalize()
        f2.close()
    return glossary_t, output_terms

def clear_search(glossary, output_gloss, ratio_gloss, list2search, i):
    words = list2search
    for word in words:
        for key in glossary:
            ratio_lev = fuzz.WRatio(word, key)
            # print(word, key, ratio_lev)
            if ratio_lev >= 87:
                term = key
                if term not in output_gloss \
                or ratio_gloss[term] < ratio_lev:
                    if glossary[key][1] != '':
                        term_var = '(' + glossary[key][1] + ') '
                    else:
                        term_var = ''
                    explanation = glossary[key][2]
                    output_string = term_var + explanation
                    output_gloss[term] = output_string
                    ratio_gloss[term] = ratio_lev
                    i += 1
    return output_gloss, ratio_gloss, i

def trash_search(glossary_t, output_gloss, 
                 ratio_gloss, list2search, i, output_terms):
    words = list2search
    for word in words:
        'ищу в грязном'
        for key in glossary_t:
            ratio_lev = fuzz.WRatio(key, word)
            if ratio_lev >= 87:
                term = key
                term_check = output_terms[term]
                if term not in output_gloss \
                or ratio_gloss[term] < ratio_lev:
                    # print(glossary[key])
                    if glossary_t[key][0] != '':
                        term_var = '(' + glossary_t[key][0] + ') '
                    else:
                        term_var = ''
                    explanation = glossary_t[key][1]
                    output_string = term_var + explanation
                    explain_found = output_gloss.values()
                    for k,v in output_terms.items():
                        if v == term_check:
                            try:
                                if output_string not in explain_found \
                                or ratio_gloss[k] < ratio_lev:
                                    output_gloss[term] = output_string
                                    ratio_gloss[term] = ratio_lev
                                    i += 1
                            except:
                                None
    return output_gloss, ratio_gloss, i

def compile_response(i, ratio_gloss, output_terms, output_gloss):
    if i!= 0:
        for_response = []
        if len(ratio_gloss.values()) > 1:
            ratio_list = list(ratio_gloss.values())
            max_ratio = max(ratio_list)
            # print(ratio_gloss, max_ratio)
            if ratio_list.count(max_ratio) > 1:
                for_response.append('Мы нашли несколько терминов, которые могут быть вам полезны.\n')
                # print('Мы нашли несколько терминов, которые могут быть вам полезны.\n')
                for term in ratio_gloss:
                    # print('я тут 1', term)
                    if ratio_gloss[term] == max_ratio:
                        parts_for_response = output_terms[term], output_gloss[term]
                        for_response_str = ' '.join(parts_for_response)
                        for_response.append(for_response_str)
                        # print(output_terms[term], output_gloss[term])
                # print(for_response)
                        # print(output_terms[term], output_gloss[term])
            else:
                for term in ratio_gloss:
                    if ratio_gloss[term] == max_ratio:
                        parts_for_response = output_terms[term], output_gloss[term]
                        for_response_str = ' '.join(parts_for_response)
                        for_response.append(for_response_str)
                        # print(output_terms[term], output_gloss[term])
        else:
            for term in ratio_gloss:
                parts_for_response = output_terms[term], output_gloss[term]
                for_response_str = ' '.join(parts_for_response)
                for_response.append(for_response_str)
                # print(output_terms[term], output_gloss[term])
    else:
        for_response = []
        with open('words_failed.csv', 'a', encoding="utf-8") as f_failed:
            f_failed.write(str(words))
            f_failed.write('\n')
        for_response.append('К сожалению, в глоссарии пока нет такого термина. Мы обязательно добавим слова по вашему запросу.')
        # print(for_response)
    return for_response


def search(words, bigramms, glossary, 
           output_terms, glossary_t):
    output_gloss = {}
    ratio_gloss = {}
    n = 0
    # поиск по чистым ячейкам
    output_gloss, ratio_gloss, n = clear_search(glossary, output_gloss, 
                                                ratio_gloss, words, n)
    print("First search")
    print(f"Found words: {n}")
    print(f"Terms&weights: {list(ratio_gloss.items())}")
    
    output_gloss, ratio_gloss, n = clear_search(glossary, output_gloss,
                                                ratio_gloss, bigramms, n)
    print("Second search")
    print(f"Found words: {n}")
    print(f"Terms&weights: {list(ratio_gloss.items())}")
    
    # поиск по грязным ячейкам
    output_gloss, ratio_gloss, i = trash_search(glossary_t,
                                                output_gloss, ratio_gloss,
                                                words, n, output_terms)
    print("Third search")
    print(f"Found words: {i}")
    print(f"Terms&weights: {list(ratio_gloss.items())}")
    
    output_gloss, ratio_gloss, i_final = trash_search(glossary_t, output_gloss,
                                                ratio_gloss, bigramms, i,
                                                output_terms)
    print("Fourth search")
    print(f"Found words: {i_final}")
    print(f"Terms&weights: {list(ratio_gloss.items())}")

    if i == 0:
        ready_response = []
        with open('words_failed.csv', 'a', encoding="utf-8") as f_failed:
            f_failed.write(str(words))
            f_failed.write('\n')
        ready_response.append('К сожалению, в глоссарии пока нет такого термина. Мы обязательно добавим слова по вашему запросу.')
        # print(for_response)
    else:
        ready_response = compile_response(i, ratio_gloss,
                                          output_terms,output_gloss)
    return '\n'.join(ready_response)

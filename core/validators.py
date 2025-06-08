def max_limit_size_upload(file):
    if file.size > 10485760:
        raise ValueError('Размер файла превышает ограниченного размера')
    else:
        return file


def ValueValidator(mark):
    if mark > 5:
        raise(f'Значение не соответствует, оценка не может быть больше 5-ти. Вы написали {mark}')
    elif mark < 2:
        raise(f'Значение не соответствует, оценка не может быть меньше 2-х. Вы написали {mark}')
    else: 
        return mark
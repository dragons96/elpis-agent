from typing import Literal


def select_lang(lang_tag: Literal['en', 'zh'] | str = 'en'):
    if lang_tag == 'en':
        from . import en
        return en
    elif lang_tag == 'zh':
        from . import zh
        return zh
    raise ValueError(f'Invalid lang: {lang_tag}')

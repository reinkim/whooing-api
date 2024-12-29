from whooing_api.category_table import CategoryTable, ItemMapping


def test_lookup():
    rules = [
        ItemMapping(name='넷플릭스서비스', spend_type='문화', display_name='Netflix'),
    ]
    tbl = CategoryTable(rules)

    cat, name = tbl.lookup('없는 값')
    assert cat == ''
    assert name == ''

    # Shorter than known prefixes
    for k in ('넷', '넷플', '넷플릭', '넷플릭스', '넷플릭스서', '넷플릭스서비'):
        cat, name = tbl.lookup(k)
        assert cat == '문화', f'lookup {k}'
        assert name == 'Netflix', f'lookup {k}'

    # Longer than known prefixes
    cat, name = tbl.lookup('넷플릭스서비스코리아')
    assert cat == '문화', f'lookup {k}'
    assert name == 'Netflix', f'lookup {k}'

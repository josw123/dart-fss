# -*- coding: utf-8 -*-
def dict_to_html(dict_data: dict, exclude=None, header=None) -> str:
    """ Dictionary를 HTML table로 변환

    Parameters
    ----------
    dict_data: dict
        dictionary data
    exclude: list of str
        dictionary 중 HTML table 변환시 제외할 키 리스
    header: list of str
        Table Header

    Returns
    -------
    str
        HTML table
    """
    style = r'''
    <style scoped>
        .dart-table tbody tr th {
            vertical-align: top;
            text-overflow: ellipsis;
        }
        .dart-table thead th {
            text-align: right;
            text-overflow: ellipsis;
        }
    </style>
    '''

    table = r'''<table border="1" class="dart-table">'''
    if header is not None:
        table += r'<thead><tr style="text-align: right;">'
        for head in header:
            table += '<th>{}</th>'.format(head)
        table += r'</tr></thead>'
    table += r'<tbody>'

    for key, value in dict_data.items():

        if exclude and key in exclude:
            continue

        if isinstance(value, list):
            table += '<tr><th>{}</th><td>'.format(key)
            if len(value) > 0:
                if isinstance(value[0], dict):
                    labels = list(value[0].keys())

                    if exclude:
                        labels = [x for x in labels if x not in exclude]

                    table += '<table style="width:100%"><thead><tr><th width="20">No.</th>'
                    for label in labels:
                        table += '<th>{}</th>'.format(label)
                    table += '</tr></thead>'
                    table += '<tbody>'
                    for idx, v in enumerate(value):
                        table += '<tr><th width="20">{}</th>'.format(idx)
                        for l in labels:
                            table += '<td>{}</td>'.format(v.get(l))
                        table += '</tr>'
                    table += '</tbody></table>'
                else:
                    table += '[{}]'.format(', '.join(value))
            table += '</td></tr>'
        else:
            table += '<tr><th>{}</th><td>{}</td></tr>'.format(key, value)
    table += '</tbody></table>'

    return style + table


# Jupyter Notebook Checker
def is_notebook():
    """ Jupyter Notebook을 사용하는지 확인하는 함수

    Returns
    -------
    bool
        Jupyter Notebook 사용시 True
    """
    try:
        from IPython import get_ipython
        if 'IPKernelApp' not in get_ipython().config:
            return False
    except Exception:
        return False
    return True


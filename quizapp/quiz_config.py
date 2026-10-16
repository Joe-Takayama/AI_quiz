QUIZ_FIELDS = {
    'python': {
        'label': 'Python',
        'themes': [
            ('list', 'リスト'),
            ('dict', '辞書'),
            ('function', '関数'),
            ('basic', '基本文法'),
        ],
    },

    'pandas': {
        'label': 'Pandas',
        'themes': [
            ('filter', 'データ抽出'),
            ('aggregate', '集計'),
            ('missing', '欠損値処理'),
            ('merge', 'データ結合'),
        ],
    },

    'sql': {
        'label': 'SQL',
        'themes': [
            ('select', 'SELECT・検索'),
            ('join', 'JOIN・結合'),
            ('group_by', 'GROUP BY・集計'),
            ('window', 'ウィンドウ関数'),
        ],
    },

    'statistics': {
        'label': '統計',
        'themes': [
            ('average', '平均・中央値'),
            ('variance', '分散・標準偏差'),
            ('probability', '確率'),
            ('test', '仮説検定'),
        ],
    },

    'machine_learning': {
        'label': '機械学習',
        'themes': [
            ('decision_tree', '決定木'),
            ('regression', '回帰'),
            ('classification', '分類'),
            ('overfitting', '過学習'),
        ],
    },

    'metrics': {
        'label': '評価指標',
        'themes': [
            ('accuracy', 'Accuracy'),
            ('precision', 'Precision'),
            ('recall', 'Recall'),
            ('f1', 'F1スコア'),
        ],
    },
}


DIFFICULTIES = [
    ('beginner', '初級'),
    ('intermediate', '中級'),
    ('advanced', '上級'),
]


QUESTION_COUNTS = [
    (5, '5問'),
    (10, '10問'),
    (20, '20問'),
]
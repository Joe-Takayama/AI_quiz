# ====================================
# 教材の文章を短く区切る
# ====================================

def split_text(text, chunk_size=500, overlap=100):

    text = text.replace('\r\n', '\n').strip()

    if not text:
        return []

    if not 0 <= overlap < chunk_size:
        raise ValueError(
            'overlapは0以上、chunk_size未満にしてください。'
        )

    chunks = []

    start = 0

    while start < len(text):

        end = start + chunk_size

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end >= len(text):
            break

        start = end - overlap

    return chunks
# =============================================== [ setting ] ==========================================================
import random
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from gensim.models.word2vec import Word2Vec
from konlpy.tag import Komoran, Okt, Kkma
from tokenizers import SentencePieceBPETokenizer # huggingface tokenization
from gensim.models import Word2Vec
from gensim.models.fasttext import FastText
from sklearn.decomposition import PCA

df = pd.read_csv("./total_everytime_data.csv").iloc[:, 1:]
df = df.iloc[0:1000, :]
# =============================================== [ preprocess ] =======================================================
def preprocessing(df, embedding_type = "FastText"):
    # + todo [ Date parsing ] ==================
    df.loc.__setitem__((df["Date"].str.contains("[0-9]{1,}[가-힣]"), "Date"), "2021-05-30")
    df.loc.__setitem__((df["Date"].str.contains("방금"), "Date"), "2021-05-30")
    df["Date"] = df["Date"].str.replace("\\s.+", "")
    df["Date"] = df["Date"].str.replace("\/", "-")

    date_form1 = str(2021) + "-" + df.loc[df["Date"].str.len() == 5]["Date"]
    df.loc.__setitem__((df["Date"].str.len() == 5, "Date"), date_form1)

    date_form2 = str(20) + df.loc[df["Date"].str.len() == 8]["Date"]
    df.loc.__setitem__((df["Date"].str.len() == 8, "Date"), date_form2)
    df["Date"] = pd.to_datetime(df["Date"], format="%Y-%m-%d")

    # + todo [ Text parsing ] ==================
    df.loc.__setitem__((df["Content"].str.contains("re :"), "Title"), "")
    df.loc.__setitem__((df["Content"].str.contains("rere :"), "Title"), "")

    df["Text"] = df["Title"] + df["Content"]
    df = df.drop(["Title", "Content"], axis=1)
    df["Text"] = df["Text"].str.replace("re :|rere :", "")

    df["Text"] = df["Text"].str.replace("(http(s)?:\/\/)([a-z0-9\w]+\.*)+[a-z0-9]{2,4}/gi", "")  # url 제거
    df["Text"] = df["Text"].str.replace("[0-9]{3}-[0-9]{4}-[0-9]{4}", "")  # 핸드폰 번호 제거
    df["Text"] = df["Text"].str.replace("[0-9]{3}-[0-9]{3}-[0-9]{4}", "")  # 과사 번호 등 전화번호 제거

    emoji_pattern = r'/[x{1F601}-x{1F64F}]/u'
    df["Text"].replace(emoji_pattern, "")  # 이모지 제거

    df["Text"] = df["Text"].str.replace("[^a-zA-Z가-힣0-9 ]", "")
    df = df[df["Text"].apply(lambda x: len(str(x))) < 3000]  # 이상치 제거

    # + todo [ POS Tokenization + word2vec ] =================
    if embedding_type == "Word2Vec":
        okt = Okt()
        tokenized_data = []
        for sentence in df["Text"]:
            tag = okt.nouns(sentence)  # 형태소 처리 ---> ["단어", "품사"]
            tag = [t for t in tag if len(t) > 1]  # 명사 태그 추출, 한글자 이상만 추출
            tokenized_data.append(tag)
        tokenizer = Word2Vec(tokenized_data, size = 5000, window = 5, min_count = 1, workers = 4, iter = 100, sg = 0)

    # + todo [ POS Tokenization + fastText ] =================
    if embedding_type == "FastText":
        okt = Okt()
        tokenized_data = []
        for sentence in df["Text"]:
            tag = okt.nouns(sentence)  # 형태소 처리 ---> ["단어", "품사"]
            tag = [t for t in tag if len(t) > 1]  # 명사 태그 추출, 한글자 이상만 추출
            tokenized_data.append(tag)
        tokenizer = FastText(tokenized_data, size= 60, window=5, min_count=5, sample=1e-2, sg=1)

    # + todo [ BPE Tokenization ] =================
    if embedding_type == "BPE":  # postional한 embedding 개념이 강하여 단어 의미 유사관계를 추론하기엔 적절하지 않은거 같은 판단.., ELMo, BERT 등 positional embedding은 문장 embedding의 성격이 강하여 적절하지 않음.)
        with open("./BPE_tokenization_text.txt", "w", encoding="utf-8")  as f:
            for line in df["Text"]:
                try:
                    f.write(line + "\n")
                except TypeError as TE:
                    print(line, TE)

        tokenizer = SentencePieceBPETokenizer()
        tokenizer.train(["./BPE_tokenization_text.txt"], vocab_size = 100000)

    return df, tokenizer

df, tokenized_data = preprocessing(df)

# ================================================ [ Visualization ] ========================================================
df_result, tokenizer = preprocessing(df, embedding_type = "FastText")
word_labels = ['진보', '좌빨', '좌파', '민주당', '복지', '민주화', '민주주의', '사회주의', '보수', '수꼴', '우파', '국민의힘', '발전', '산업화', '자유주의', '자본주의']
semantically_similar_words = {words: [item[0] for item in tokenizer.wv.most_similar([words], topn = 10)] for words in word_labels}

all_similar_words = sum([[k] + v for k, v in semantically_similar_words.items()], [])
word_vectors = tokenizer.wv[all_similar_words]
pca = PCA(n_components = 2)
p_comps = pca.fit_transform(word_vectors)
word_names = all_similar_words

plt.figure(figsize = (18, 10))
plt.scatter(p_comps[:, 0], p_comps[:, 1], c = 'red')
for word_names, x, y in zip(word_names, p_comps[:, 0], p_comps[:, 1]) :
    plt.annotate(word_names, xy = (x+0.06, y+0.03), xytext = (0, 0), textcoords = 'offset points')
print(plt.show())

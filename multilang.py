"""
HAS-Core :: SDIR multilingual tokenizer

Extends SDIR beyond English. Supported: English, Chinese, French, Spanish,
German. The language is detected automatically; Chinese is segmented with
jieba, Latin-script languages split on whitespace. Each language has its own
stop-word list so common function words do not distort the signals.

This is an interface layer only. It does not touch the core detection logic
(region-split, baseline lock). It just turns text in several languages into a
comparable token stream, so the same structural read-out applies across them.
"""
from __future__ import annotations
import re

# minimal stop-word lists per language (function words that carry little signal)
_STOP = {
    "en": {"the","a","an","and","or","of","to","in","is","it","that","this",
           "for","on","with","as","are","was","be","by","at","from"},
    "fr": {"le","la","les","un","une","des","et","ou","de","du","à","en","est",
           "il","elle","que","ce","pour","dans","sur","avec","au","aux"},
    "es": {"el","la","los","las","un","una","y","o","de","del","a","en","es",
           "que","este","para","con","por","su","se","lo","al"},
    "de": {"der","die","das","ein","eine","und","oder","von","zu","in","ist",
           "es","dass","für","auf","mit","als","im","dem","den","des"},
    "zh": {"的","了","和","是","在","我","有","他","这","个","们","中","来",
           "上","为","以","于","其","而","与","之","也"},
}

_LATIN = {"en", "fr", "es", "de"}


def detect_language(text: str) -> str:
    """Lightweight language detection. Chinese by character range; among Latin
    scripts, by characteristic stop-words. Defaults to English."""
    # Chinese: any CJK characters
    if re.search(r"[\u4e00-\u9fff]", text):
        return "zh"
    low = text.lower()
    words = set(re.findall(r"[a-zàâçéèêëîïôûùüÿñæœ]+", low))
    # score each Latin language by stop-word overlap
    best, best_score = "en", 0
    for lang in ("fr", "es", "de", "en"):
        score = len(words & _STOP[lang])
        if score > best_score:
            best, best_score = lang, score
    return best


def tokenize(text: str, lang: str = None) -> list:
    """Tokenize text in the detected (or given) language, dropping stop-words."""
    if lang is None:
        lang = detect_language(text)
    if lang == "zh":
        import jieba
        toks = [t.strip() for t in jieba.cut(text) if t.strip()]
        toks = [t for t in toks if t not in _STOP["zh"] and not re.match(r"^\W+$", t)]
        return toks
    # Latin scripts
    low = text.lower()
    toks = re.findall(r"[a-zàâçéèêëîïôûùüÿñæœ]+", low)
    stop = _STOP.get(lang, _STOP["en"])
    return [t for t in toks if t not in stop]


def tokenize_batch(texts: list) -> tuple:
    """Tokenize a batch, detecting the dominant language of the batch so all
    documents are treated consistently. Returns (list_of_token_lists, lang)."""
    if not texts:
        return [], "en"
    # detect dominant language from a sample
    sample = " ".join(texts[:20])
    lang = detect_language(sample)
    return [tokenize(t, lang) for t in texts], lang

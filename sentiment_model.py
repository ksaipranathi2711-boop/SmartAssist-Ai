"""Lightweight lexicon-based sentiment."""
POS = {"good","great","awesome","love","excellent","amazing","perfect","happy","thanks","thank","nice","fast","helpful"}
NEG = {"bad","terrible","worst","hate","angry","slow","broken","useless","awful","problem","issue","not working","disappointed"}
def analyze_sentiment(text:str)->str:
    t = text.lower()
    p = sum(1 for w in POS if w in t)
    n = sum(1 for w in NEG if w in t)
    if p > n: return "positive"
    if n > p: return "negative"
    return "neutral"

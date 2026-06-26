import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline

date_antrenare = [
    "Patrula a ajuns la destinație cu bine.",
    "Avem nevoie de un raport de stare.",
    "Vremea este senină, vizibilitate bună.",
    "Confirm recepția echipamentului.",
    "Ne retragem la bază conform programului.",
    "Suntem pe poziții și așteptăm ordine.",
    "Comunicare stabilă, niciun incident raportat.",

    "Suntem atacați, cerem sprijin aerian imediat!",
    "Avem răniți grav, trimiteți medicul urgent!",
    "Inamicul a spart linia de apărare, retragere tactică!",
    "Bomba a fost detectată, aveți grijă!",
    "SOS, ambuscadă în sectorul 4!",
    "Foc inamic puternic, nu ne putem mișca!",
    "Atenție, prezență inamică neidentificată în perimetru!"
]

etichete = [0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1]

model_nlp = make_pipeline(TfidfVectorizer(lowercase=True, strip_accents='unicode'), MultinomialNB())

print("Se antrenează modelul tactic AI...")
model_nlp.fit(date_antrenare, etichete)

test = ["Avem un soldat rănit grav, ajutor!"]
predictie = model_nlp.predict(test)
print(f"Test predicție: {'URGENȚĂ' if predictie[0] == 1 else 'NORMAL'}")

joblib.dump(model_nlp, 'model_tactic_nlp.pkl')
print("Modelul a fost salvat ca 'model_tactic_nlp.pkl'.")
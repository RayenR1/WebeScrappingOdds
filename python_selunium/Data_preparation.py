import pandas as pd
from sklearn.preprocessing import OneHotEncoder
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

# Chargement des données
data = pd.read_csv('matches.csv', sep=';', encoding='ISO-8859-1')

# Suppression des valeurs manquantes
data = data.dropna()

# Séparation des caractéristiques (X) et de la cible (y)
X = data.drop(columns=['Gangnant', 'Score Domicile', 'Score Extérieur'])
y = data['Gangnant']  # Ne pas traiter la colonne cible

# Encodage des variables catégorielles et scaling des variables numériques
numerical_columns = X.select_dtypes(include=['float64', 'int64']).columns
categorical_columns = X.select_dtypes(include=['object']).columns

# OneHotEncoding pour les variables catégorielles avec gestion des catégories inconnues
onehot_encoder = OneHotEncoder(sparse_output=False, drop='first', handle_unknown='ignore')
encoded_categorical_data = onehot_encoder.fit_transform(X[categorical_columns])
encoded_categorical_df = pd.DataFrame(encoded_categorical_data,
                                      columns=onehot_encoder.get_feature_names_out(categorical_columns))

# Standardisation des variables numériques
scaler = StandardScaler()
X[numerical_columns] = scaler.fit_transform(X[numerical_columns])

# Fusion des données encodées
X_encoded = pd.concat([X[numerical_columns].reset_index(drop=True),
                       encoded_categorical_df.reset_index(drop=True)], axis=1)

# Réduction de dimensions avec PCA (pour garder 95% de la variance)
pca = PCA(n_components=0.95)
X_reduced = pca.fit_transform(X_encoded)

# Séparation en données d'entraînement (85%) et de test (15%)
X_train, X_test, y_train, y_test = train_test_split(X_reduced, y, test_size=0.15, random_state=42)

# Création et entraînement du modèle de régression logistique
model = LogisticRegression(max_iter=1000)
model.fit(X_train, y_train)

# Prédiction sur les données de test
y_pred = model.predict(X_test)

# Calcul du taux de réussite (accuracy)
accuracy = accuracy_score(y_test, y_pred)
print(f"Le taux de réussite du modèle sur les données de test est : {accuracy * 100:.2f}%")

# Boucle de test avec des entrées utilisateur
print("\n=== Tester le modèle avec des données personnalisées ===")
print("Entrez les valeurs pour chaque variable, séparées par des virgules (ou 'exit' pour quitter) :\n")
print("Format: Saison, Championat, Date, Heure, Équipe Domicile, Équipe Extérieur, Cote 1, Cote X, Cote 2")

while True:
    user_input = input("Données: ")
    if user_input.lower() == 'exit':
        print("Fin du programme.")
        break

    # Séparation des entrées par des virgules
    input_values = user_input.split(',')

    # Vérification que le nombre d'entrées est correct
    if len(input_values) != 9:
        print("Erreur : veuillez entrer exactement 9 valeurs.")
        continue

    # Extraction et nettoyage des données
    saison, championat, date, heure, equipe_domicile, equipe_exterieur, cote_1, cote_x, cote_2 = map(str.strip, input_values)

    # Conversion des cotes en float
    try:
        cote_1 = float(cote_1)
        cote_x = float(cote_x)
        cote_2 = float(cote_2)
    except ValueError:
        print("Erreur : les cotes doivent être des nombres.")
        continue

    # Création d'une liste pour les nouvelles données d'entrée
    input_data = [cote_1, cote_x, cote_2]

    # Création des données catégorielles
    categorical_input = [saison, championat, date, heure, equipe_domicile, equipe_exterieur]

    # Encodage et standardisation des nouvelles données
    encoded_categorical_input = onehot_encoder.transform([categorical_input])
    scaled_numerical_input = scaler.transform([input_data])

    # Fusionner les nouvelles données encodées
    full_input = pd.concat([pd.DataFrame(scaled_numerical_input), pd.DataFrame(encoded_categorical_input)], axis=1)

    # Réduction avec PCA
    reduced_input = pca.transform(full_input)

    # Prédiction avec le modèle
    prediction = model.predict(reduced_input)
    print(f"\nLe modèle prédit un résultat de : {'Gagnant' if prediction[0] == 1 else 'Perdant'}\n")

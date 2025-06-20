import pandas as pd

from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.tree import DecisionTreeClassifier

from database import Connection

class Model:
    @staticmethod
    def train():
        label_encoders = {}

        # Lê toda a tabela "germancredit" do banco de dados como DataFrame
        df = pd.read_sql("SELECT * FROM germancredit", Connection.engine)

        # Detecta colunas categóricas (strings) e numéricas (int/float)
        categorical_columns = df.select_dtypes(include=['object']).columns.tolist()
        numerical_columns = df.select_dtypes(include=['int64', 'float64']).columns.tolist()

        # Remove a coluna alvo ('kredit') da lista de colunas numéricas, se presente
        if 'kredit' in numerical_columns:
            numerical_columns.remove('kredit')

        # Codifica variáveis categóricas usando LabelEncoder e armazena os encoders para uso futuro
        for col in categorical_columns:
            le = LabelEncoder()
            df[col] = le.fit_transform(df[col])
            label_encoders[col] = le

        # Separa variáveis de entrada (X) e variável alvo (y)
        x = df.drop('kredit', axis=1)
        y = df['kredit']

        # Lista os nomes das features para referência futura
        feature_names = x.columns.tolist()

        # Divide o dataset em treino (80%) e teste (20%) com estratificação da classe alvo
        x_train, x_test, y_train, y_test = train_test_split(
            x, y, test_size=0.2, random_state=42, stratify=y
        )

        print(f"Dados pré-processados. Conjunto de treino: {x_train.shape}, Conjunto de teste: {x_test.shape}")

        # Cria e treina o classificador de árvore de decisão
        model = DecisionTreeClassifier(random_state=42)
        model.fit(x_train, y_train)

        # Faz predições no conjunto de teste
        y_pred = model.predict(x_test)

        # Calcula métricas de avaliação do modelo
        accuracy = accuracy_score(y_test, y_pred)
        conf_matrix = confusion_matrix(y_test, y_pred)
        class_report = classification_report(y_test, y_pred)

        # Exibe resultados de avaliação no console
        print(f"\n{'=' * 50}")
        print("AVALIAÇÃO DO MODELO")
        print(f"{'=' * 50}")
        print(f"Acurácia: {accuracy:.4f}")
        print(f"\nMatriz de Confusão:")
        print(conf_matrix)
        print(f"\nRelatório de Classificação:")
        print(class_report)
        print(f"{'=' * 50}")

        # Retorna o modelo treinado, encoders e nomes das features para uso posterior
        return {
            "model": model,
            "label_encoders": label_encoders,
            "feature_names": feature_names
        }

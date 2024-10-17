import streamlit as st
import time

# Fonction de réponse à la question
def get_response(question):
    # Simule un traitement de la question
    response = f"La réponse à votre question '{question}' est : 'Voici une réponse générée.'"
    return response

# Page principale
def main():
    st.title("Prototype - Question / Réponse")

    # Entrée pour la question de l'utilisateur
    question = st.text_input("Posez votre question ici :")

    # Démarre le chronomètre
    if question:
        start_time = time.time()

        # Génère la réponse
        response = get_response(question)

        # Calcule le temps écoulé
        end_time = time.time()
        elapsed_time = end_time - start_time

        # Affichage de la réponse
        st.subheader("Réponse :")
        st.write(response)

        # Affichage du délai (timer)
        st.subheader("Délai pour obtenir la réponse :")
        st.write(f"{elapsed_time:.2f} secondes")

    # Rubrique "Informations diverses" pour le débogage
    st.sidebar.title("Informations diverses")
    st.sidebar.write("Vous pouvez ajouter ici des informations pour le débogage.")
    st.sidebar.write("Exemple d'infos :")
    st.sidebar.write("- Question posée : " + (question if question else "Aucune question posée"))
    st.sidebar.write("- Temps écoulé pour générer la réponse : " + (f"{elapsed_time:.2f} secondes" if question else "N/A"))

if __name__ == '__main__':
    main()

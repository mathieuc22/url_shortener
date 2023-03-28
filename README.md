# URL Shortener

Ce projet est un réducteur de lien / minimiseur d'URL simple, développé avec FastAPI. Il comprend une API pour créer, récupérer et lister les URL raccourcies. Ce README contient des instructions pour installer, exécuter et déployer l'application.

## Prérequis

- Python 3.7 ou supérieur
- Git (optionnel, pour cloner le dépôt)

## Installation

1. Clonez ce dépôt (ou téléchargez-le manuellement) :

```
git clone https://github.com/mathieuc22/url_shortener.git
```

2. Accédez au répertoire du projet :

```
cd url_shortener
```

3. Créez un environnement virtuel pour isoler les dépendances de votre projet :

```
python -m venv venv
```

4. Activez l'environnement virtuel :

- Sous Linux et macOS :

```
source venv/bin/activate
```

- Sous Windows :

```
venv\Scripts\activate
```

5. Installez les dépendances :

```
pip install -r requirements.txt
```

## Utilisation

1. Exécutez l'application FastAPI localement avec uvicorn :

```
uvicorn main:app --reload
```

2. Accédez à l'interface Swagger pour explorer et tester l'API :

```
http://127.0.0.1:8000/docs
```

## Déploiement

Pour déployer cette application sur un serveur ou un service cloud, suivez les instructions spécifiques à la plateforme choisie. Voici quelques options pour déployer votre API :

- [Heroku](https://www.heroku.com/)
- [Google Cloud Run](https://cloud.google.com/run)
- [AWS Lambda](https://aws.amazon.com/fr/lambda/)
- [Microsoft Azure Functions](https://azure.microsoft.com/fr-fr/services/functions/)

## Frontend

Pour créer une interface utilisateur pour votre réducteur de lien, vous pouvez utiliser des frameworks tels que React, Vue ou Angular, ou simplement utiliser du HTML, CSS et JavaScript pour créer une page statique. Cette page doit être en mesure de consommer l'API que vous avez créée avec FastAPI.

Une fois le frontend développé, vous pouvez héberger la page statique sur des services tels que GitHub Pages, Netlify ou Vercel.

## Licence

Ce projet est sous licence MIT. Consultez le fichier [LICENSE](LICENSE) pour plus d'informations.

Mise en place du projet django 

Je vais vous présenter mon rapport sur la mise en place du projet Django pour la gestion des flux bancaires. Ce projet a été réalisé dans le cadre de ma SAE et vise à créer une application web permettant aux agents de gérer les flux bancaires de manière efficace et sécurisée.

Pour réaliser ce projet, nous devions réaliser des microservices qui sont :
- Un microservice pour l'authentification des utilisateurs
- Un microservice pour la gestion des agents et des flux bancaires
- Un microservice pour la gestion des interfaces utilisateur et agent
- Un microservice pour le logging et la communication entre les services

J'ai utilisé Django REST Framework pour créer les APIs, NATS pour le logging et la communication entre les services, et TailwindCSS pour le design des interfaces.

Etant seul dans ce projet, j'ai appris à gérer l'ensemble du processus de développement, de la mise en place de l'infrastructure à la mise en production. J'ai également appris à utiliser des outils tels que Docker pour containeriser l'application, et Git pour le versionnage du code.

A présent je vais vous présenter les différentes étapes de la mise en place du projet de manière chronologique.

0. Mise en place de l'infrastructure
Dans un premier temps, j'ai repris le sujet et essayé de comprendre les besoins du projet. J'ai ensuite réaliser un schéma de l'architecture du projet, en identifiant les différents microservices à mettre en place et les interactions entre eux. J'ai également mis en place un environnement de développement avec Docker pour faciliter le déploiement et la gestion des dépendances.

J'ai créé un dépôt Git pour le projet et j'ai commencé à structurer le code en suivant les bonnes pratiques de développement Django. J'ai également mis en place un fichier `docker-compose.yml` pour gérer les différents services nécessaires au projet, tels que la base de données, le serveur web et le serveur NATS.

Dans la première phase de développement j'ai voulu travailler sur des workers locaux des api afin d'avoir des log clair et précis fourni par Python et Django. J'ai donc mis en place un environnement de développement local avec Docker, en utilisant des conteneurs pour la base de données et le serveur NATS.

1. Mise en place de l'environnement (A revoir)

Dans la suite logique de la mise en place du projet j'ai également essayé de mettre en place un environnement de développement local avec l'utilisation 

2. Développement de l'api d'authentification (A ajouter le JWT)



3. Mise en place de l'api des agents sur la gestion des flux bancaires

4. Mise en place des interfaces pour l'utilisateur

5. Mise en place de l'interface pour les agents

6. Ajout du logging avec nats

7. Ajout du dashboard nats

8. Tests unitaires et d'intégration

9. Documentation technique et utilisateur

10. Déploiement et mise en production

11. Sécurité et gestion des permissions

12. Suivi de la performance et optimisation


- Avantage d'utiliser des sous-classes dans les models
- Utilisation de `getattr` pour accéder aux attributs
- Utilisation des fonctions dans les serializers afin de faire des tests avant la création de l'objet
- Utilisation de la fonction `get_object_or_404` pour récupérer un objet ou renvoyer une erreur 404
- Utilisation de TailwindCSS pour le design des interfaces
- Utilisation de NATS pour le logging et la communication entre les services
- Utilisation de Django REST Framework pour la création des APIs
- Création d'un wrapper pour les vues afin de gérer les permissions et l'authentification via le token Basic Django 
- Utilisation de `django-cors-headers` pour gérer les CORS
- Utilisation de la logique validation action pour traiter les données des serializers
https://www.django-rest-framework.org/tutorial/1-serialization/ > Validation des données
https://www.django-rest-framework.org/api-guide/serializers/#field-level-validation => Validation personnalisée
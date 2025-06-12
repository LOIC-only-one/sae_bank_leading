Mise en place du projet django 

0. Mise en place de l'infrastructure

1. Mise en place de l'environnement

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
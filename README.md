gantt
    title Projet bancaire – Gantt final avec technologies (2 au 23 Juin 2025)
    dateFormat  YYYY-MM-DD
    excludes    weekends

    %% ---------------- INFRASTRUCTURE & CONTAINERS ----------------
    section Infra & Conteneurisation
    Choix stack (Django REST / FastAPI + MySQL)   :done, s1, 2025-06-02, 1d
    Dockerisation des services API                :s2, after s1, 1d
    Dockerisation base MySQL                      :s3, after s2, 1d
    Création d’un réseau Docker (bridge)          :s4, after s3, 1d
    Déploiement service NATS via Docker           :s5, after s4, 1d
    Tests communication inter-conteneurs          :s6, after s5, 1d

    %% ---------------- AUTHENTIFICATION ----------------
    section Authentification
    API d'inscription / login (JWT)               :a1, 2025-06-05, 1d
    Intégration backend Django REST/FastAPI       :a2, after a1, 1d
    Sécurisation accès API (permissions)          :a3, after a2, 1d

    %% ---------------- COMPTES CLIENT ----------------
    section Gestion clients & opérations
    Modèle utilisateur, comptes, opérations       :b1, 2025-06-08, 1d
    API dépôt / retrait / virement                :b2, after b1, 1d
    Historique et solde actuel (API + DB)         :b3, after b2, 1d

    %% ---------------- GESTION AGENTS ----------------
    section Gestion des agents bancaires
    API validation création de comptes            :c1, 2025-06-10, 1d
    API validation opérations clients             :c2, after c1, 1d
    Interface lecture comptes (montant, date...)  :c3, after c2, 1d
    Authentification et droits des agents         :c4, after c3, 1d

    %% ---------------- LOGGING ----------------
    section Logging NATS & persistances
    Intégration NATS publisher dans API           :d1, 2025-06-12, 1d
    Développement du service subscriber (NATS)    :d2, after d1, 1d
    Sauvegarde des logs dans MySQL                :d3, after d2, 1d
    Ajout filtres date/type pour consultation     :d4, after d3, 1d

    %% ---------------- DASHBOARD ----------------
    section Tableau de bord & statistiques
    API stats : nb opérations, utilisateurs, etc. :e1, 2025-06-15, 1d
    Interface dashboard (texte/JSON, REST)        :e2, after e1, 1d

    %% ---------------- LIVRABLES ----------------
    section Livrables finaux
    Rédaction rapport individuel                  :f1, 2025-06-17, 2d
    Validation compétences & réalisations         :f2, after f1, 1d
    Finalisation dépôt GitHub (projet + README)   :f3, 2025-06-20, 1d
    Préparation présentation orale (slides)       :f4, 2025-06-20, 1d
    Soutenance finale (15–20 min)                 :f5, 2025-06-23, 1d

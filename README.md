```mermaid
gantt
    title Projet bancaire - Gantt (2 au 23 Juin)
    dateFormat  YYYY-MM-DD
    excludes    weekends
    %% Définition des groupes
    section Planification & Infra
    Définition de l'architecture             :done, a1, 2025-06-02, 2d
    Mise en place de l'infrastructure VM    :done, a2, after a1, 2d
    Conteneurisation (Docker + NATS)        :a3, after a2, 2d

    section Authentification
    Authentification site/API               :b1, 2025-06-06, 2d
    Création de compte utilisateur          :b2, after b1, 2d

    section Gestion des comptes privés
    Modèle des comptes                      :c1, 2025-06-10, 1d
    Dépôt / Retrait                         :c2, after c1, 2d
    Virement entre comptes                  :c3, after c2, 2d

    section Gestion Agent Bancaire
    Validation opérations                   :d1, 2025-06-10, 3d
    Visualisation comptes clients           :d2, after d1, 2d
    Validation création de compte           :d3, after d2, 2d
    Ajout infos : solde, date op            :d4, after d3, 1d

    section Gestion des logs (NATS)
    Mise en place service logging           :e1, 2025-06-10, 2d
    Intégration NATS dans APIs              :e2, after e1, 2d
    Stockage logs dans base de données      :e3, after e2, 2d

    section Dashboard & Statistiques
    Création dashboard logs/ops             :f1, 2025-06-17, 2d
    Sélecteur de période/type de log        :f2, after f1, 1d
    Statistiques d'opérations               :f3, after f2, 1d

    section Finalisation et tests
    Tests unitaires et fonctionnels         :g1, 2025-06-19, 2d
    Corrections et améliorations            :g2, after g1, 1d
    Rendu Moodle et documentation           :g3, 2025-06-23, 1d
```

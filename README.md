```mermaid
gantt
    title Projet bancaire – Planification Juin 2025
    dateFormat  YYYY-MM-DD

    section Planification & Analyse
    Prise en main du sujet & découpage des tâches     :done, 2025-06-02, 1d
    Recherche techno (Docker, Django/FastAPI, NATS)   :done, 2025-06-03, 1d
    Choix final des techno + maquette archi           :done, 2025-06-04, 2d

    section Infrastructure technique
    Init VM & environnement Docker                    :2025-06-06, 1d
    Conteneurisation MySQL + NATS                     :2025-06-07, 1d
    Base projet API Django/FastAPI                    :2025-06-08, 1d
    Configuration réseau interne Docker + tests       :2025-06-09, 1d

    section Authentification
    API login/signup (DRF ou FastAPI)                 :2025-06-10, 2d
    Sécurisation JWT / permissions                    :2025-06-12, 1d

    section Gestion clients
    API dépôt / retrait / virement                    :2025-06-13, 2d
    Historique client + soldes                        :2025-06-15, 1d
    Tests unitaires + intégration                     :2025-06-16, 1d

    section Agents bancaires
    Back-office agent : validation opérations         :2025-06-17, 1d
    Vue lecture comptes clients                       :2025-06-18, 1d
    Ajout infos : solde, dernière op, etc.            :2025-06-19, 1d

    section Logs & Monitoring
    Intégration Publisher NATS dans APIs              :2025-06-20, 1d
    Service Listener log & insertion BDD              :2025-06-21, 1d
    Sélecteur période + type de logs                  :2025-06-22, 1d

    section Dashboard
    API statistique opérations / logs                 :2025-06-23, 1d
    Interface Web de consultation (JSON/text)         :2025-06-24, 1d

    section Documentation & Rendus
    Rédaction rapport individuel                      :2025-06-20, 3d
    Lien GitHub propre avec commits et README         :2025-06-23, 1d
    Création slides + support oral                    :2025-06-24, 1d
    Présentation orale / soutenance                   :2025-06-25, 1d

```

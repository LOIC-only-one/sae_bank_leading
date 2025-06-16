## 🚀 Installation du projet Bank Leading

### 🛠️ Prérequis
- **Python** 3.8 ou supérieur
- **pip** (gestionnaire de paquets Python)
- **Git** (optionnel, pour cloner le dépôt)
- **Docker**
- **Docker Compose**

---

### 📦 Étapes d'installation

1. **Cloner le dépôt (optionnel) :**
    ```bash
    git clone https://github.com/LOIC-only-one/sae_bank_leading.git
    ```

2. **Se placer dans le dossier du projet :**
    ```bash
    cd sae_bank_leading
    ```

3. **Installer Docker :**  
    Suivez le guide officiel selon votre système d'exploitation :  
    👉 [Guide d'installation Docker](https://docs.docker.com/get-docker/)

4. **Installer Docker Compose :**  
    Suivez le guide officiel selon votre système d'exploitation :  
    👉 [Guide d'installation Docker Compose](https://docs.docker.com/compose/install/)

5. **Construire et lancer les conteneurs :**
    ```bash
    docker-compose up --build
    ```

6. **Accéder à l'application :**  
    Une fois les conteneurs démarrés, ouvrez votre navigateur à l'adresse :
    ```
    http://localhost:8001
    ```

---

> 💡 **Astuce :**  
> Si vous lancez le projet en local, utilisez `localhost:8001`.  
> Sur un serveur distant, remplacez `localhost` par l'adresse IP ou le nom de domaine du serveur.

---

### 📋 Logs des conteneurs

Pour consulter les logs d'un conteneur :
```bash
docker logs -f <container_id>
```

# APIZIT fastapi — API adversariale bornée

Lancer une API de test locale et observer des comportements adversariaux contrôlés.
Fixture de sécurité pour une future campagne APIZIT **dev** ; aucun lancement AWS
n'est effectué par le dépôt ou sa CI. Ce projet est autonome et ne dépend pas du checkout APIZIT.

## Démarrage local

```text
python -m venv .venv
# Activer .venv selon votre shell, puis :
python -m pip install -r requirements-dev.txt
python -m uvicorn app:app --host 127.0.0.1 --port 8080
```

Dans un second terminal : `curl http://127.0.0.1:8080/health`.
Lire les scénarios avant leurs appels. Utiliser des données synthétiques et un seul
processus, sans reloader. Redémarrer uniquement pour une nouvelle série contrôlée.

## Bornes et interprétation

Les limites sont celles de cette fixture, **pas des limites commerciales APIZIT**.
100 admissions par processus ; Flask/FastAPI limitent aussi à 2 requêtes actives.
Le compteur n'est pas global entre instances et ne rend pas un déploiement public sûr
face à un trafic illimité. La future campagne doit borner appels, durée et nombre d'instances.
Une limite applicative atteinte ne prouve pas qu'APIZIT applique la même protection.
Les probes ci-dessous sont volontairement modestes : elles vérifient des mécanismes,
sans chercher à atteindre les quotas cloud ou provoquer un DoS.

Les neuf références Light/Heavy/private conservent leur contrat et leur health check immédiat.
Cette extension security possède son propre contrat de 15 routes.

## Scénarios

| Test | Endpoint | Risque | Borne |
| --- | --- | --- | --- |
| [Health dépendance simulée](security-tests/health/README.md) | `GET /health` | LOW | Attente asynchrone de 50 ms ; aucune connexion |
| [Entrées volumineuses](security-tests/request-probe/README.md) | `POST /request` | MEDIUM | Body 64 KiB, 64 headers, 16 KiB headers, query 8 KiB ; lecture 1 s |
| [JSON imbriqué](security-tests/json-depth/README.md) | `POST /json-depth` | MEDIUM | Profondeur 32, body 64 KiB ; contrôle avant json.loads |
| [Expansion gzip](security-tests/compression/README.md) | `POST /compression` | MEDIUM | 64 KiB compressés et décompressés ; un seul membre gzip |
| [Réponse volumineuse](security-tests/large-response/README.md) | `GET /response` | MEDIUM | 1 MiB fixe de données synthétiques |
| [Streaming borné](security-tests/stream/README.md) | `GET /stream` | MEDIUM | 32 fragments de 4 KiB ; attente totale programmée 320 ms |
| [Multiples headers](security-tests/headers/README.md) | `GET /headers` | LOW | 32 headers synthétiques de 128 caractères |
| [Codes applicatifs ambigus](security-tests/codes/README.md) | `GET /codes` | LOW | Liste fixe : 200,400,402,403,404,409,429,500,503 |
| [Tâche ASGI après body](security-tests/background/README.md) | `POST /background` | LOW | 1 tâche de 200 ms par appel ; 2 requêtes actives maximum |
| [État global ASGI](security-tests/state/README.md) | `GET /state` | LOW | 1 compteur et 1 identifiant de processus |
| [DNS localhost](security-tests/dns/README.md) | `GET /dns` | LOW | 1 résolution de localhost, attente 1 s ; aucun hostname fourni par le client |
| [Connexions locales](security-tests/connections/README.md) | `GET /connections` | MEDIUM | Désactivé par défaut ; 4 GET localhost:8766, timeout 300 ms, deadline 1 s |
| [Récursion HTTP simulée](security-tests/recursion/README.md) | `GET /recursion` | LOW | 3 niveaux, 3 GET vers un peer ASGI en mémoire |
| [Logs synthétiques](security-tests/logs/README.md) | `POST /logs` | LOW | 16 lignes fixes, aucun contenu de requête |
| [Health erreur volumineuse](security-tests/health-error/README.md) | `GET /health-error` | MEDIUM | Erreur 500 avec exactement 1 MiB synthétique |

## Vérification

```text
ruff check .
ruff format --check .
pytest -q
```

La CI Linux/Windows utilise des doubles pour AWS et HTTP sortant. Les tests
font réellement fonctionner les petites charges CPU/mémoire et les routes ; le
test Flask lance un enfant Python bénin. Aucun paiement, déploiement ou appel AWS.
Un scan local APIZIT détecte les routes ; ce résultat n'est pas une attestation de sécurité.

Le rapport global, les protections analysées et le protocole de campagne se trouvent
dans le dépôt plateforme : `docs/SECURITY_TEST_APIS.md`.

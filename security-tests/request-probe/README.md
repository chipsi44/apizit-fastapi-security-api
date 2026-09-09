# Entrées volumineuses

## Objectif et abus représenté

Amplifier le coût de parsing via body, headers et paramètres multiples. Ce scénario permet d'isoler ce comportement pendant une future
qualification, avec des données synthétiques.

## Comportement et endpoints

`POST /request` — Body 64 KiB, 64 headers, 16 KiB headers, query 8 KiB ; lecture 1 s.

```text
curl -X POST http://127.0.0.1:8080/request
```

## Observation attendue sur APIZIT

Envoyer uniquement du synthétique, observer tailles/compteurs et provenance du 413 ou 431.

## Protection à vérifier et réaction idéale

Limites HTTP du gateway et de l'adaptateur. Le résultat doit rester borné et correctement attribué au
client, sans effet sur un autre workspace. Une observation locale ne démontre
pas cette propriété dans AWS.

## Risque et précautions

Niveau : **MEDIUM**, dans les bornes de la fixture. Lire le README racine,
utiliser un environnement jetable, commencer par un appel et ne pas utiliser
de load generator. Pas de production, de paiement, de données réelles, de
lecture de secrets ou de cible tierce. Le plafond par processus ne remplace
pas un budget global lors d'une campagne multi-instance.

Les cas synthétiques exacts (bornes, contenu tronqué, valeurs invalides) sont
reproductibles via `pytest -q tests/test_api.py`. Le client de test est en mémoire ;
il ne mesure pas les limites du serveur HTTP ni d'API Gateway.


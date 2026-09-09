# Health erreur volumineuse

## Objectif et abus représenté

Faire lire un corps d'erreur volumineux par le worker de santé. Ce scénario permet d'isoler ce comportement pendant une future
qualification, avec des données synthétiques.

## Comportement et endpoints

`GET /health-error` — Erreur 500 avec exactement 1 MiB synthétique.

```text
curl -X GET http://127.0.0.1:8080/health-error
```

## Observation attendue sur APIZIT

Configurer ce chemin comme health check lors de la future campagne ; observer mémoire, logs et statut de release.

## Protection à vérifier et réaction idéale

Lecture bornée des erreurs HTTP et échec de promotion fidèle. Le résultat doit rester borné et correctement attribué au
client, sans effet sur un autre workspace. Une observation locale ne démontre
pas cette propriété dans AWS.

## Risque et précautions

Niveau : **MEDIUM**, dans les bornes de la fixture. Lire le README racine,
utiliser un environnement jetable, commencer par un appel et ne pas utiliser
de load generator. Pas de production, de paiement, de données réelles, de
lecture de secrets ou de cible tierce. Le plafond par processus ne remplace
pas un budget global lors d'une campagne multi-instance.

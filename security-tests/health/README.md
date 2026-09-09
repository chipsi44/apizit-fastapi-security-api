# Health dépendance simulée

## Objectif et abus représenté

Représenter un health check dépendant d'un service lent. Ce scénario permet d'isoler ce comportement pendant une future
qualification, avec des données synthétiques.

## Comportement et endpoints

`GET /health` — Attente asynchrone de 50 ms ; aucune connexion.

```text
curl -X GET http://127.0.0.1:8080/health
```

## Observation attendue sur APIZIT

Mesurer durée ; cette simulation ne valide pas une politique réseau.

## Protection à vérifier et réaction idéale

Timeout et état de santé. Le résultat doit rester borné et correctement attribué au
client, sans effet sur un autre workspace. Une observation locale ne démontre
pas cette propriété dans AWS.

## Risque et précautions

Niveau : **LOW**, dans les bornes de la fixture. Lire le README racine,
utiliser un environnement jetable, commencer par un appel et ne pas utiliser
de load generator. Pas de production, de paiement, de données réelles, de
lecture de secrets ou de cible tierce. Le plafond par processus ne remplace
pas un budget global lors d'une campagne multi-instance.

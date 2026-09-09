# État global ASGI

## Objectif et abus représenté

Conserver un résultat après la réponse. Ce scénario permet d'isoler ce comportement pendant une future
qualification, avec des données synthétiques.

## Comportement et endpoints

`GET /state` — 1 compteur et 1 identifiant de processus.

```text
curl -X GET http://127.0.0.1:8080/state
```

## Observation attendue sur APIZIT

Lire le compteur après /background ; vérifier séparation entre processus.

## Protection à vérifier et réaction idéale

Isolation de l'état global. Le résultat doit rester borné et correctement attribué au
client, sans effet sur un autre workspace. Une observation locale ne démontre
pas cette propriété dans AWS.

## Risque et précautions

Niveau : **LOW**, dans les bornes de la fixture. Lire le README racine,
utiliser un environnement jetable, commencer par un appel et ne pas utiliser
de load generator. Pas de production, de paiement, de données réelles, de
lecture de secrets ou de cible tierce. Le plafond par processus ne remplace
pas un budget global lors d'une campagne multi-instance.
